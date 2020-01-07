import re
import datetime

_identifier_regex = re.compile("[A-Za-z_]\w*")


class primitive_tokens:
	kInlined = 0 #content that has no type, no shape or recognizable form
	kWhitespace = 1 #tabs vs spaces
	kComment = 2 #comment line/blocks

	kIdentifier = 3
	kCharSequance = 4 #...
	kNumber = 5 #floats and ints
	kString = 6 # "high" 'low'

class token_flags:
	k_identifier_flag = 1<<0
	k_string_flag = 1<<1

	k_conditional_flag = 1<<2 #all controll expressions (if,ifdef,else, etc), these require evaluation
	k_trivial_flag = 1<<3 #expressions that are not part of evaluation
	k_id_str_argument_flag = 1<<4 #expressions with one argument that can be string or identifier

	k_command_flag = 1<<5 #all known expressions that are part of evaluation
	k_no_error = 1<<6 #some commands are more strict, this flag is in case an alternavie should be used

	k_endl_flag = 1<<7 #there is at least one newline in the token value.
	k_child_token = 1<<8 #token holds in location the source token

	k_impostor = 1<<9 #for tokens that start wtih `#` but represent primitive tokens
	k_blank = 1<<10 #blank tokens is `#/`

	k_first_mask_index = 11
	k_first_mask = (1<<(k_first_mask_index + 0)) | (1<<(k_first_mask_index + 1)) | (1<<(k_first_mask_index + 2))

class precompiler_tokens:
	#k_index = 6

	#for parsing 'define' arguments
	k_scope_push = 10
	k_scope_pop = 11

	k_define = 12 #add define with `identifier` name
	k_undefine = 13

	k_if_defined = 14 #with identifier
	k_if_not_defined = 15 #with identifier

	k_if = 16 #if with python syntax
	k_else_if = 17 #else if ...
	k_endif = 18 #close if/elif block
	k_else = 19  #else for #if/#elif block

	k_collapse = 22 #reasignes a defines content with it's processed content
	k_cwstrip = 23 #remove whitespaces and comments

	k_source = 24 #legacy
	k_run = 25 #run python code


	#string or identifier; if identifier is used then the content of the define is taken without processing
	k_error = 26 #stopes execution
	k_include = 27 #file is tokenized and added in the evaluation stack
	k_inline_include = 28 #file content is added directly to the output (without processing)
	k_inline_eval = 29 #python eval, output is added to output
	k_inline_str = 30 #if string then inlines unboxed string; if identfier then inlines the define value
	k_load_config = 31 #loads an ini file and creates global defines from that ini


##########################################################################################################


def CreateUserDefineSourceToken(define_name,string_value):
	return (precompiler_tokens.k_define, 0, (define_name,None,string_value), ["user", -1] )

##########################################################################################################

#used to report errors in a generic source code file
class SourceCodeError(Exception):
	def __init__(self, tok, message):
		Exception.__init__(self,message)
		self.tok = tok

##########################################################################################################

def FormatFileLocation(abs_source_file,line):
	return abs_source_file + "(" + str(line + 1) + ")"

def RaiseErrorAtLocation(source_file,line,message,variable_message):
	raise SourceCodeError(None,"\nError:\n>" + FormatFileLocation(source_file,line) + "-> " + variable_message + "\n.> " + message)

def RaiseErrorAtToken(tok,message,variable_message):
	(tok_flags,_,tok_value,source_loc) = tok
	location = ">" + FormatFileLocation(source_loc[0],source_loc[1]) + "->" + str(tok_value)
	while (tok_flags & token_flags.k_child_token) != 0:
		tok = source_loc[2]
		#print(tok)
		(tok_flags,_,tok_value,source_loc) = tok
		location = location + "\n>" + FormatFileLocation(source_loc[0],source_loc[1]) + "->" + str(tok_value)
	if variable_message == None:
		variable_message = ""
	raise SourceCodeError(tok,"\nError:\n" + location + "->" + variable_message + "\n> " + message)


##########################################################################################################
#processing utils

def TokListJoinValue(tok_list):
	return "".join([value[0] for (_,_,value,_) in tok_list])

def RelocateTokenAtExpandedToken(original_token,token_with_new_location):
	expanded_location = TokSource(token_with_new_location)
	new_location = [expanded_location[0],expanded_location[1],original_token]

	(tok_flags, tok_tp, tok_value, tok_loc) = original_token

	new_flags = tok_flags | token_flags.k_child_token
	return (new_flags, tok_tp, tok_value, new_location)


def TokSource(tok):
	(_,_,_,location) = tok
	return location

def ValidateIdentifier(str_value):
	global _identifier_regex
	return _identifier_regex.match(str_value)

#transforms a string into a string with escape sequances.
def BoxStringHigh(str_value):
	return str_value.translate(str.maketrans({
		"\n":  "\\n",
		"\t":  "\\t",
		"\\":  "\\\\",
		"\"":  "\\\"",
	}))


#replaces escape sequances with actual characters
def UnboxString(str_value):
	result = str_value
	if(result[0] == '\"' or result[0] == '\''):
		result = result[1:]
	if(result[-1] == '\"' or result[-1] == '\''):
		result = result[:-1]

	return bytes(result, 'utf-8').decode('unicode_escape')

###########################################################################################################
###########################################################################################################
###########################################################################################################


def isComment(toktype):
	if(toktype == primitive_tokens.kComment):
		return True
	return False

def GetNowTimeString():
	return datetime.datetime.now().strftime('%H:%M %b/%d/%Y')

###########################################################################################################
###########################################################################################################
###########################################################################################################

#helper classes for generated source code.
class SourceAssemblerStack(object):
	def __init__(self,_parent_writer):
		self.parent_writer = _parent_writer

	def WriteRawStr(self,str_value):
		if self.parent_writer != None:
			self.parent_writer.WriteRawStr(str_value)

	def Write(self,tok_tuple):
		if self.parent_writer != None:
			self.parent_writer.Write(tok_tuple)

	def Close(self):
		if self.parent_writer != None:
			self.parent_writer.Close()

	def GetName(self):
		if self.parent_writer:
			return self.parent_writer.GetName()


class BufferedFileAssembler(object):
	def __init__(self,os_file_handle,abs_file_path,size_limit):
		self.buffer = []
		self.out_file_handle = os_file_handle
		self.size = size_limit
		self.name = abs_file_path

	def WriteRawStr(self,str_value):
		self.out_file_handle.write(str_value)

	def Write(self,tok_tuple):
		_tok_value = tok_tuple[2]
		self.buffer.append(_tok_value[0])
		if (len(self.buffer) > self.size):
			for c in self.buffer:
				self.out_file_handle.write(c)
			self.buffer.clear()

	def Close(self):
		for c in self.buffer:
			#print(">" + c)
			self.out_file_handle.write(c)
		self.out_file_handle.close()

	def GetName(self):
		return self.name


class EmptyAssembler(object):
	def __init__(self):
		pass

	def Write(self,tok_tuple):
		pass

	def Close(self):
		pass

	def GetName(self):
		return "empty"
###########################################################################################################

class WhitespaceMinimizer(SourceAssemblerStack):
	def __init__(self,parent_writer):
		SourceAssemblerStack.__init__(self,parent_writer)

		self.white_buffer = ""

		self.last_solid_token = None

		self.join_tokens = False
		self.collapse_whitespaces = False
		self.collapse_endlines = False


	def can_remove_whitespaces_between(self,fist_roken,second_token):
		return False

	def Write(self,tok_tuple):

		#append to whitespace buffer
		if(tok_tuple[1] == primitive_tokens.kWhitespace):
			tokvalue = tok_tuple[2][0]
			self.white_buffer = self.white_buffer + tokvalue;
			return

		#not a whitespace, we process the existing whitespace buffer
		if(self.white_buffer != ""):
			if self.join_tokens == True and self.last_solid_token != None:
				if self.can_remove_whitespaces_between(self.last_solid_token,tok_tuple) == True:
					self.white_buffer = ""
					return;

			if self.collapse_whitespaces == True:
				if self.white_buffer.find("\n") != -1:
					self.white_buffer = "\n"
				else:
					self.white_buffer = " "
			elif self.collapse_endlines == True:
				end = self.white_buffer.rfind("\n")
				if end != -1:
					if self.last_solid_token == None:
						end += 1
					self.white_buffer = self.white_buffer[end:]

			self.parent_writer.Write( (0, primitive_tokens.kWhitespace,[self.white_buffer]) )
			self.white_buffer = ""

		self.last_solid_token = tok_tuple
		self.parent_writer.Write(tok_tuple)


class WhitespaceMinimizerDefault(WhitespaceMinimizer):
	def __init__(self,parent_writer):
		WhitespaceMinimizer.__init__(self,parent_writer)

	def can_remove_whitespaces_between(self,fist_roken,second_token):
		if(fist_roken[1] == primitive_tokens.kIdentifier and second_token[1] == primitive_tokens.kIdentifier):
			return False
		if(fist_roken[1] == primitive_tokens.kNumber and second_token[1] == primitive_tokens.kNumber):
			return False
		if(fist_roken[1] == primitive_tokens.kInlined or second_token[1] == primitive_tokens.kInlined):
			return False

		return True



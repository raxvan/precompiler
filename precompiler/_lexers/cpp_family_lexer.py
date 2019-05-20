
#Original lexers located in precompiler/precompiler/_lexers

import re
import ply.lex as lex
import precompiler._utils.pc_utils as _pc_utils

g_lexer = None
g_processed_source_name = None


def RaiseError(t,message,variable_message):
	return _pc_utils.RaiseErrorAtLocation(g_processed_source_name,t.lexer.lineno,message,variable_message);

def CreateLineCommentFromText(text_message):
	return "//" + text_message

###########################################################################################################
#one word without arguments; must be added in CMD_WORD regex
#syntax: `#command`
g_trivial_commands = {
	'endif' : 'ENDIF',
	'else' : 'ELSE',
}

#syntax: `#command IDENTIFIER`
g_cmd_with_id_arg = {
	'ifdef' : 'IFDEF',
	'ifndef' : 'IFNDEF',
	'undef' : 'UNDEF',

	'source' : 'PRAGMA',

	'collapse' : 'COLLAPSE',
	'cwstrip' : 'CWSTRIP'
}

#syntax: `#command "path"` or `#command IDENTIFIER`
g_exp_with_string_or_id_arg = {
	'error' : 'ERR',

	'include' : 'INCL', #regular include
	'inline-include' : 'INL_INCL', #include without processing

	'inline' : 'INL_STR', #unbox the string (replace all \n with newlines, etc)

	'config' : 'CONFIG',

}

g_cmd_line_eat = {
	'run' : 'RUN', #eats entire line
	'inline-run' : 'INL_EVL', #execute code inplace
}

g_exp_with_string_args = {
	#...
}

g_trivial_tokens = [
	'WHITE',
	'WHITE_MULTILINE',
	'LINE_COMMENT', #has line ending
	'LINE_COMMENT_MULTILINE',
	'BLOCK_COMMENT',
	'BLOCK_COMMENT_MULTILINE',

	'NUMBER',
	'STRING',

	'CMD_SEPARATOR_EMPTY',
	'CH',
	'CH_BEGIN_0',
	'CH_END_0',
	'CH_BEGIN_1',
	'CH_END_1',
	'CH_BEGIN_2',
	'CH_END_2',
]

g_separators = [
	'CMD_TAB',
	'CMD_SPACE',
	'CMD_NEWLINE',
	'CMD_CAPTURE_WHITE',
	'CMD_FUUUUUU'
]

tokens = g_trivial_tokens + [
	'ID',

	'CMD_DEF', #eats entire line
	'CMD_REDEF', #eats entire line

	'CMD_IF',
	'CMD_IF_MULTILINE', #has line ending
	'CMD_ELIF',
	'CMD_ELIF_MULTILINE', #has line ending

	'CMD_ON_LINE_INTERNAL', #eats entire line

	'TOK_STRING_HIGH', #syntax "string"
	'TOK_STRING_LOW', #syntax 'stirng'

	'TOK_FLOAT_INTERNAL',

	'TOK_CH_EX_INTERNAL', #internal use; to bypass characters that start a comment; also handles CH_END,CH_BEGIN

	'CMD_IF_ELSEIF', #syntax: `#(if|elif) PYTHON-CONDITION (: | \n)`
	'CMD_WORD', #internal use for g_trivial_commands
	#CMD_WORD must have a higher priority than CMD_WITH_ID_ARG_INTERNAL and CMD_WITH_STRING_ARG_HIGH_INTERNAL/LOW!

	'CMD_WITH_ID_ARG_INTERNAL', #internal use
	'CMD_WITH_STRING_ARG_HIGH_INTERNAL', #internal use
	'CMD_WITH_STRING_ARG_LOW_INTERNAL', #internal use
	'CH_SEPARATOR_INTERNAL', #internal use


] + list(set(
	list(g_trivial_commands.values()) +
	list(g_cmd_with_id_arg.values()) +
	list(g_exp_with_string_or_id_arg.values()) +
	list(g_exp_with_string_args.values()) +
	list(g_cmd_line_eat.values()) +
	list(g_separators)
))

_prep_flags = _pc_utils.token_flags
_prep_tokens = _pc_utils.primitive_tokens
_prep_tokens_ex = _pc_utils.precompiler_tokens

_prep_map = {
	'WHITE' : ( _prep_tokens.kWhitespace, _prep_flags.k_trivial_flag ),
	'WHITE_MULTILINE' : ( _prep_tokens.kWhitespace, _prep_flags.k_trivial_flag | _prep_flags.k_endl_flag ),

	'CMD_FUUUUUU' : ( _prep_tokens.kWhitespace, _prep_flags.k_blank),

	'CMD_SEPARATOR_EMPTY' : ( _prep_tokens.kWhitespace, _prep_flags.k_trivial_flag | _prep_flags.k_impostor), #whitespace impostor
	'CMD_TAB' : ( _prep_tokens.kWhitespace, _prep_flags.k_trivial_flag | _prep_flags.k_impostor ) , #whitespace impostor
	'CMD_SPACE' : ( _prep_tokens.kWhitespace, _prep_flags.k_trivial_flag | _prep_flags.k_impostor ) , #whitespace impostor
	'CMD_NEWLINE' : ( _prep_tokens.kWhitespace, _prep_flags.k_trivial_flag | _prep_flags.k_impostor | _prep_flags.k_endl_flag ) , #whitespace impostor
	'CMD_CAPTURE_WHITE' : ( _prep_tokens.kWhitespace, _prep_flags.k_trivial_flag | _prep_flags.k_impostor ) , #whitespace impostor
	'CMD_CAPTURE_WHITE_MULTILINE' : ( _prep_tokens.kWhitespace, _prep_flags.k_trivial_flag | _prep_flags.k_impostor | _prep_flags.k_endl_flag) , #whitespace impostor

	'LINE_COMMENT' : ( _prep_tokens.kComment, _prep_flags.k_trivial_flag ),
	'LINE_COMMENT_MULTILINE' : ( _prep_tokens.kComment, _prep_flags.k_trivial_flag | _prep_flags.k_endl_flag ),
	'BLOCK_COMMENT' : ( _prep_tokens.kComment, _prep_flags.k_trivial_flag ),
	'BLOCK_COMMENT_MULTILINE' : ( _prep_tokens.kComment, _prep_flags.k_trivial_flag | _prep_flags.k_endl_flag),

	'NUMBER' : ( _prep_tokens.kNumber, _prep_flags.k_trivial_flag ),
	'STRING' : ( _prep_tokens.kString, _prep_flags.k_trivial_flag ),

	'CH' : ( _prep_tokens.kCharSequance, _prep_flags.k_trivial_flag ),

	'CH_BEGIN_0' : ( _prep_tokens_ex.k_scope_push, _prep_flags.k_trivial_flag | (1 << (_prep_flags.k_first_mask_index + 0) ) ),
	'CH_END_0' : ( _prep_tokens_ex.k_scope_pop, _prep_flags.k_trivial_flag | (1 << (_prep_flags.k_first_mask_index + 0) ) ),
	'CH_BEGIN_1' : ( _prep_tokens_ex.k_scope_push, _prep_flags.k_trivial_flag | (1 << (_prep_flags.k_first_mask_index + 1) ) ),
	'CH_END_1' : ( _prep_tokens_ex.k_scope_pop, _prep_flags.k_trivial_flag | (1 << (_prep_flags.k_first_mask_index + 1) ) ),
	'CH_BEGIN_2' : ( _prep_tokens_ex.k_scope_push, _prep_flags.k_trivial_flag | (1 << (_prep_flags.k_first_mask_index + 2) ) ),
	'CH_END_2' : ( _prep_tokens_ex.k_scope_pop, _prep_flags.k_trivial_flag | (1 << (_prep_flags.k_first_mask_index + 2) ) ),


	'ID' : ( _prep_tokens.kIdentifier, 0 ), #we consider id's non trivial in this case because

	#non trivial stuff:
	'RUN' : ( _prep_tokens_ex.k_run, _prep_flags.k_command_flag),
	'INL_EVL' : ( _prep_tokens_ex.k_inline_eval, _prep_flags.k_command_flag ),

	'CMD_DEF' : ( _prep_tokens_ex.k_define, _prep_flags.k_command_flag | _prep_flags.k_endl_flag),
	'CMD_REDEF' : ( _prep_tokens_ex.k_define, _prep_flags.k_command_flag | _prep_flags.k_no_error | _prep_flags.k_endl_flag ),

	'CMD_IF' : ( _prep_tokens_ex.k_if, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag ),
	'CMD_IF_MULTILINE' : ( _prep_tokens_ex.k_if, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag | _prep_flags.k_endl_flag ),

	'CMD_ELIF' : ( _prep_tokens_ex.k_else_if, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag ),
	'CMD_ELIF_MULTILINE' : ( _prep_tokens_ex.k_else_if, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag | _prep_flags.k_endl_flag),

	'ENDIF' : ( _prep_tokens_ex.k_endif, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag ),
	'ELSE' : ( _prep_tokens_ex.k_else, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag ),
	'IFDEF' : ( _prep_tokens_ex.k_if_defined, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag ),
	'IFNDEF' : ( _prep_tokens_ex.k_if_not_defined, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag ),

	'UNDEF' : ( _prep_tokens_ex.k_undefine, _prep_flags.k_command_flag ),
	'PRAGMA' : ( _prep_tokens_ex.k_source, _prep_flags.k_command_flag ),
	'COLLAPSE' : ( _prep_tokens_ex.k_collapse, _prep_flags.k_command_flag ),
	'CWSTRIP' : ( _prep_tokens_ex.k_cwstrip, _prep_flags.k_command_flag ),
	'ERR' : ( _prep_tokens_ex.k_error, _prep_flags.k_id_str_argument_flag | _prep_flags.k_command_flag ),
	'INCL' : ( _prep_tokens_ex.k_include, _prep_flags.k_id_str_argument_flag | _prep_flags.k_command_flag ),
	'INL_INCL' : ( _prep_tokens_ex.k_inline_include, _prep_flags.k_id_str_argument_flag | _prep_flags.k_command_flag ),
	'INL_STR' : ( _prep_tokens_ex.k_inline_str, _prep_flags.k_id_str_argument_flag | _prep_flags.k_command_flag ),
	'CONFIG' : ( _prep_tokens_ex.k_load_config, _prep_flags.k_id_str_argument_flag | _prep_flags.k_command_flag ),
}

###########################################################################################################

def t_TOK_STRING_HIGH(t):
	r'"(?:\\.|[^"\\])*"'
	t.type = 'STRING'
	t.value = [t.value]
	return t

def t_TOK_STRING_LOW(t):
	r'\'(?:\\.|[^\'\\])*\''
	t.type = 'STRING'
	t.value = [t.value]
	return t

def t_TOK_FLOAT_INTERNAL(t):
	r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?'
	t.type = 'NUMBER'
	t.value = [t.value]
	return t

def t_NUMBER(t):
	r'\d+'
	t.value = [t.value]
	return t

def t_ID(t):
	r'[A-Za-z_]\w*'
	t.value = [t.value]
	return t

def _internal_define_handler(t,name,def_name,data):
	if data != None:
		data = data.strip(' \t\n\r')
		if data == "":
			data = None
	if t.value.endswith("\n"):
		t.lexer.lineno += 1
	t.value = [t.value,def_name,data]
	if name == "redefine":
		t.type = "CMD_REDEF"
	return t

#multiline, eats entire line except `\n`
def t_CMD_DEF(t):
	r'\#[ \t]*(?P<name>define|redefine)[ \t]+(?P<defid>[A-Za-z_]\w*)(?:\n|(?P<content>.+?\n))'
	name = t.lexer.lexmatch.group('name');
	def_name = t.lexer.lexmatch.group('defid')
	data = t.lexer.lexmatch.group('content');
	return _internal_define_handler(t,name,def_name,data)

#multiline, eats entire line except `\n`
def t_CMD_ON_LINE_INTERNAL(t):
	r'\#[ \t]*(?P<name>run|inline-run)[ \t]+(?P<content>[^\n]+)(?#filler_comment_for_regex_length_________________)'
	name = t.lexer.lexmatch.group('name')
	data = t.lexer.lexmatch.group('content');
	t.type = g_cmd_line_eat.get(name,None)
	if t.type == None:
		RaiseError(t,"Invalid precompiler command!",name)

	if data != None:
		data = data.strip(' \t\n\r')
		if data == "":
			data = None
	if t.value.endswith("\n"):
		t.lexer.lineno += 1
	t.value = [t.value,data]
	return t

#multiline, eats entire line except `\n` or `:`
def t_CMD_IF_ELSEIF(t):
	r'\#[ \t]*(?P<name>if|elif)[ \t](?P<exp>.+?[:\n])'
	func = t.lexer.lexmatch.group('name')
	exp = t.lexer.lexmatch.group('exp')
	if t.value.endswith("\n"):
		t.lexer.lineno += 1
		t.type = 'CMD_IF_MULTILINE' if func == "if" else 'CMD_ELIF_MULTILINE'
	else:
		t.type = 'CMD_IF' if func == "if" else 'CMD_ELIF'

	t.value = [t.value,exp.strip(': \t\n\r')]
	return t

def t_CMD_WORD(t):
	r'\#[ \t]*(?P<name>endif|else)(?#filler_comment_for_regex_length_________________________)'
	nm = t.lexer.lexmatch.group('name')
	t.type = g_trivial_commands.get(nm,None)
	t.value = [t.value]
	assert(t.type != None)
	return t

def t_CMD_FUUUUUU(t):
	r'\$'
	t.value = [""]
	return t

def t_CH_SEPARATOR_INTERNAL(t):
	r'\#\\(?P<exp>[tsnwe])(?P<extra>[ \t\n]+)(?#filler_comment_for_regex_length_________________________________________________________)'

	newline_count = t.value.count("\n")
	if newline_count != 0:
		t.lexer.lineno += newline_count

	exp = t.lexer.lexmatch.group('exp')
	if exp == 'w':
		vl = t.lexer.lexmatch.group('extra')
		if newline_count != 0:
			t.type = 'CMD_CAPTURE_WHITE_MULTILINE'
		else:
			t.type = 'CMD_CAPTURE_WHITE'
		t.value = [vl]
	elif exp == 't':
		t.value = ["\t"]
		t.type = 'CMD_TAB'
	elif exp == 's':
		t.value = [" "]
		t.type = 'CMD_SPACE'
	elif exp == 'n':
		t.value = ["\n"]
		t.type = 'CMD_NEWLINE'
	elif exp == 'e':
		t.value = [""]
		t.type = 'CMD_SEPARATOR_EMPTY'
	else:
		RaiseError(t,"Invalid token while searching for separator!",t.value)
	return t

def _internal_EXP_WITH_STRING_ARG(t,string_terminator):
	exp = t.lexer.lexmatch.group('exp')
	str_value = string_terminator + t.lexer.lexmatch.group('str_arg') + string_terminator
	t.type = g_exp_with_string_or_id_arg.get(exp,None)
	if t.type != None:
		t.value = [t.value,str_value,_prep_flags.k_string_flag]
		return t
	t.type = g_exp_with_string_args.get(exp,None)
	if t.type != None:
		t.value = [t.value,str_value]
		return t
	t.type = "?"

	RaiseError(t,"Invalid precompiler command!",exp)

def t_CMD_WITH_STRING_ARG_LOW_INTERNAL(t):
	r'\#[ \t]*(?P<exp>[A-Za-z_][-\w]*)[ \t]+\'(?P<str_arg>(?:\\.|[^\'\\])*)\''
	return _internal_EXP_WITH_STRING_ARG(t,'\'')

def t_CMD_WITH_STRING_ARG_HIGH_INTERNAL(t):
	r'\#[ \t]*(?P<exp>[A-Za-z_][-\w]*)[ \t]+"(?P<str_arg>(?:\\.|[^"\\])*)"'
	return _internal_EXP_WITH_STRING_ARG(t,"\"")

def t_CMD_WITH_ID_ARG_INTERNAL(t):
	r'\#[ \t]*(?P<exp>[a-zA-Z_][-\w]*)[ \t]+(?P<name>[a-zA-Z_]\w*)'
	exp = t.lexer.lexmatch.group('exp')
	name = t.lexer.lexmatch.group('name')

	if exp == "define" or exp == "redefine":
		#this happens when define has no line ending
		#TODO: handle special case in some other way
		return _internal_define_handler(t,exp,name,None)

	t.type = g_cmd_with_id_arg.get(exp,None)
	if t.type != None:
		t.value = [t.value,name]
		return t
	t.type = g_exp_with_string_or_id_arg.get(exp,None)
	if t.type != None:
		t.value = [t.value,name,_prep_flags.k_identifier_flag]
		return t
	t.type = "?"
	RaiseError(t,"Invalid token while searching for command!",exp)

###########################################################################################################

def t_WHITE(t):
	r'[ \t\r\n]+'

	newline_count = t.value.count("\n")
	if newline_count != 0:
		t.lexer.lineno += newline_count
		t.type = 'WHITE_MULTILINE'
	t.value = [t.value]
	return t

#multiline, eats entire line except `\n`
def t_LINE_COMMENT(t):
	r'//[^\n]*(?#filler_comment_for_regex_length_________________)'
	newline_count = t.value.count("\n")
	if newline_count != 0:
		t.lexer.lineno += newline_count
		t.type = 'LINE_COMMENT_MULTILINE'
	t.value = [t.value]
	return t

#multiline
def t_BLOCK_COMMENT(t):
	r'(/\*(.|\n)*?(\*/))(?#filler_comment_for_regex_length_________________)'
	newline_count = t.value.count("\n")
	if newline_count != 0:
		t.lexer.lineno += newline_count
		t.type = 'BLOCK_COMMENT_MULTILINE'
	t.value = [t.value]
	return t




def t_CH(t):
	r'[-`~!%^&*+=|;:\\.,?/><]+'
	t.value = [t.value]
	return t

#used here not to match characters in line comments or comment block
_ch_type_map = {
	'(' : 'CH_BEGIN_0',
	')' : 'CH_END_0',
	'[' : 'CH_BEGIN_1',
	']' : 'CH_END_1',
	'{' : 'CH_BEGIN_2',
	'}' : 'CH_END_2',
}

def t_TOK_CH_EX_INTERNAL(t):
	r'[(){}\[\]]'
	t.type = _ch_type_map[t.value]
	t.value = [t.value]
	return t

def t_error(t):
	end = t.value.find("\n")
	RaiseError(t,"Unknown syntax!","`" + t.value[:end] + "`")

def t_eof(t):
	return None

###########################################################################################################

g_lexer = lex.lex()

def StringTokenize(source_identifier,content, parent_token ):
	if(content == ""):
		return []

	global g_processed_source_name
	global _prep_map

	g_processed_source_name = source_identifier
	g_lexer.input(content)

	result = []

	g_lexer.lineno = 0

	while True:
		current_line = g_lexer.lineno
		tok_loc = [source_identifier,current_line]
		tok = g_lexer.token()

		if not tok:
			break

		translated_tok = _prep_map.get(tok.type,None)
		if translated_tok == None:
			continue;

		(tok_tp,tok_flags) = translated_tok

		#if tok_flags & _prep_flags.k_endl_flag:
		#	tok_loc.append(g_lexer.lineno - current_line)

		if parent_token != None:
			tok_flags = tok_flags | _prep_flags.k_child_token
			tok_loc.append(parent_token)

		result.append(( tok_flags, tok_tp, tok.value, tok_loc ))

	g_processed_source_name = None

	return result

###########################################################################################################

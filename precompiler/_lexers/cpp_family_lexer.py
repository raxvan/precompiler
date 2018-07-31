import re
import ply.lex as lex
import precompiler._utils.pc_utils as _pc_utils

g_lexer = None
g_processed_source_name = None


def RaiseError(message,variable_message):
	global g_current_line
	return _pc_utils.RaiseErrorAtLocation(g_processed_source_name,g_current_line,message,variable_message);

###########################################################################################################
#one word without arguments; must be added in EXP_TRIVIAL regex
#syntax: `#command`
g_trivial_statements = {
	'endif' : 'ENDIF',
	'else' : 'ELSE',

}

#syntax: `#command IDENTIFIER`
g_exp_with_id_arg = {
	'ifdef' : 'IFDEF',
	'ifndef' : 'IFNDEF',
	'undef' : 'UNDEF',

	'source' : 'PRAGMA',

	'colapse' : 'COLAPSE',
	'cwstrip' : 'CWSTRIP'
}

#syntax: `#command "path"` or `#command IDENTIFIER`
g_exp_with_string_or_id_arg = {
	'error' : 'ERR',

	'include' : 'INCL', #regular include
	'inline-include' : 'INL_INCL', #include without processing

	'inline-run' : 'INL_EVL', #execute code inplace
	'inline' : 'INL_STR', #unbox the string (replace all \n with newlines, etc)
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

	'CH_NOP',
	'CH',
	'CH_BEGIN_0',
	'CH_END_0',
	'CH_BEGIN_1',
	'CH_END_1',
	'CH_BEGIN_2',
	'CH_END_2',
]

tokens = g_trivial_tokens + [
	'ID',

	'DEF', #eats entire line
	'REDEF', #eats entire line
	'RUN', #eats entire line


	'IF',
	'IF_MULTILINE', #has line ending
	'ELIF',
	'ELIF_MULTILINE', #has line ending


	'TOK_IF_ELSEIF', #syntax: `#(if|elif) PYTHON-CONDITION (: | \n)`
	'TOK_STRING_HIGH', #syntax "string"
	'TOK_STRING_LOW', #syntax 'stirng'

	'TOK_FLOAT_INTERNAL',

	'TOK_CH_EX', #internal use; to bypass characters that start a comment; also handles CH_END,CH_BEGIN

	'EXP_TRIVIAL', #internal use for g_trivial_statements
	#EXP_TRIVIAL must have a higher priority than EXP_WITH_ID_ARG and EXP_WITH_STRING_ARG_HIGH/LOW!

	'EXP_WITH_ID_ARG', #internal use
	'EXP_WITH_STRING_ARG_HIGH', #internal use
	'EXP_WITH_STRING_ARG_LOW', #internal use

] + list(set(
	list(g_trivial_statements.values()) +
	list(g_exp_with_id_arg.values()) +
	list(g_exp_with_string_or_id_arg.values()) +
	list(g_exp_with_string_args.values())
))

_prep_flags = _pc_utils.token_flags
_prep_tokens = _pc_utils.primitive_tokens
_prep_tokens_ex = _pc_utils.precompiler_tokens

_prep_map = {
	'WHITE' : ( _prep_tokens.kWhitespace, _prep_flags.k_trivial_flag ),
	'WHITE_MULTILINE' : ( _prep_tokens.kWhitespace, _prep_flags.k_trivial_flag | _prep_flags.k_endl_flag ),
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
	'RUN' : ( _prep_tokens_ex.k_run, _prep_flags.k_command_flag | _prep_flags.k_endl_flag),
	'DEF' : ( _prep_tokens_ex.k_define, _prep_flags.k_command_flag | _prep_flags.k_endl_flag),
	'REDEF' : ( _prep_tokens_ex.k_define, _prep_flags.k_command_flag | _prep_flags.k_no_error | _prep_flags.k_endl_flag ),

	'IF' : ( _prep_tokens_ex.k_if, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag ),
	'IF_MULTILINE' : ( _prep_tokens_ex.k_if, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag | _prep_flags.k_endl_flag ),

	'ELIF' : ( _prep_tokens_ex.k_else_if, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag ),
	'ELIF_MULTILINE' : ( _prep_tokens_ex.k_else_if, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag | _prep_flags.k_endl_flag),

	'ENDIF' : ( _prep_tokens_ex.k_endif, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag ),
	'ELSE' : ( _prep_tokens_ex.k_else, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag ),
	'IFDEF' : ( _prep_tokens_ex.k_if_defined, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag ),
	'IFNDEF' : ( _prep_tokens_ex.k_if_not_defined, _prep_flags.k_conditional_flag | _prep_flags.k_command_flag ),

	'UNDEF' : ( _prep_tokens_ex.k_undefine, _prep_flags.k_command_flag ),
	'PRAGMA' : ( _prep_tokens_ex.k_source, _prep_flags.k_command_flag ),
	'COLAPSE' : ( _prep_tokens_ex.k_colapse, _prep_flags.k_command_flag ),
	'CWSTRIP' : ( _prep_tokens_ex.k_cwstrip, _prep_flags.k_command_flag ),
	'ERR' : ( _prep_tokens_ex.k_error, _prep_flags.k_id_str_argument_flag | _prep_flags.k_command_flag ),
	'INCL' : ( _prep_tokens_ex.k_include, _prep_flags.k_id_str_argument_flag | _prep_flags.k_command_flag ),
	'INL_INCL' : ( _prep_tokens_ex.k_inline_include, _prep_flags.k_id_str_argument_flag | _prep_flags.k_command_flag ),
	'INL_EVL' : ( _prep_tokens_ex.k_inline_eval, _prep_flags.k_id_str_argument_flag | _prep_flags.k_command_flag ),
	'INL_STR' : ( _prep_tokens_ex.k_inline_str, _prep_flags.k_id_str_argument_flag | _prep_flags.k_command_flag ),
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

#multiline, eats entire line except `\n`
def t_DEF(t):
	r'\#[ \t]*(?P<name>define|redefine)[ \t]+(?P<defid>[A-Za-z_]\w*)(?:\n|(?P<content>.+?\n))'
	name = t.lexer.lexmatch.group('name');
	data = t.lexer.lexmatch.group('content');
	if data != None:
		data = data.strip(' \t\n\r')
		if data == "":
			data = None
	if t.value.endswith("\n"):
		t.lexer.lineno += 1
	t.value = [t.value,t.lexer.lexmatch.group('defid'),data]
	if name == "redefine":
		t.type = "REDEF"
	return t

#multiline, eats entire line except `\n`
def t_RUN(t):
	r'\#[ \t]*run[ \t]+(?P<content>.+?\n)(?#filler_comment_for_regex_length_________________)'

	data = t.lexer.lexmatch.group('content');
	if data != None:
		data = data.strip(' \t\n\r')
		if data == "":
			data = None
	if t.value.endswith("\n"):
		t.lexer.lineno += 1
	t.value = [t.value,data]
	return t

#multiline, eats entire line except `\n` or `:`
def t_TOK_IF_ELSEIF(t):
	r'\#[ \t]*(?P<name>if|elif)[ \t](?P<exp>.+?[:\n])'
	func = t.lexer.lexmatch.group('name')
	exp = t.lexer.lexmatch.group('exp')
	if t.value.endswith("\n"):
		t.lexer.lineno += 1
		t.type = 'IF_MULTILINE' if func == "if" else 'ELIF_MULTILINE'
	else:
		t.type = 'IF' if func == "if" else 'ELIF'

	t.value = [t.value,exp.strip(': \t\n\r')]
	return t

def t_EXP_TRIVIAL(t):
	r'\#[ \t]*(?P<name>endif|else|endl)(?#filler_comment_for_regex_length_________________-----)'
	nm = t.lexer.lexmatch.group('name') #to elevate priority of EXP_TRIVIAL
	if nm == 'endl':
		#lexer hack
		t.type = 'WHITE_MULTILINE'
		t.value = ['\n']
	else:
		t.type = g_trivial_statements.get(nm,None)
		t.value = [t.value]
		assert(t.type != None)
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

	RaiseError("Invalid precompiler expression!",exp)

def t_EXP_WITH_STRING_ARG_LOW(t):
	r'\#[ \t]*(?P<exp>[A-Za-z_][-\w]*)[ \t]+\'(?P<str_arg>(?:\\.|[^\'\\])*)\''
	return _internal_EXP_WITH_STRING_ARG(t,'\'')

def t_EXP_WITH_STRING_ARG_HIGH(t):
	r'\#[ \t]*(?P<exp>[A-Za-z_][-\w]*)[ \t]+"(?P<str_arg>(?:\\.|[^"\\])*)"'
	return _internal_EXP_WITH_STRING_ARG(t,"\"")

def t_EXP_WITH_ID_ARG(t):
	r'\#[ \t]*(?P<exp>[a-zA-Z_][-\w]*)[ \t]+(?P<name>[a-zA-Z_]\w*)'
	exp = t.lexer.lexmatch.group('exp')
	name = t.lexer.lexmatch.group('name')
	t.type = g_exp_with_id_arg.get(exp,None)
	if t.type != None:
		t.value = [t.value,name]
		return t
	t.type = g_exp_with_string_or_id_arg.get(exp,None)
	if t.type != None:
		t.value = [t.value,name,_prep_flags.k_identifier_flag]
		return t
	t.type = "?"
	RaiseError("Invalid token!",exp)

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
	r'//(?:.|\n)*(?#filler_comment_for_regex_length_________________)'
	newline_count = t.value.count("\n")
	if newline_count != 0:
		t.lexer.lineno += newline_count
		t.type = 'LINE_COMMENT_MULTILINE'
	t.value = [t.value]
	return t

#multiline
def t_BLOCK_COMMENT(t):
	r'(/\*(.|\n|.)*?(\*/))(?#filler_comment_for_regex_length_________________)'
	newline_count = t.value.count("\n")
	if newline_count != 0:
		t.lexer.lineno += newline_count
		t.type = 'BLOCK_COMMENT_MULTILINE'
	t.value = [t.value]
	return t

def t_CH_NOP(t):
	r'\#[-.>]'
	t.value = [t.value]
	return t

def t_CH(t):
	r'[-`~!@$%^&*+=|;:\\.,?/><]+'
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

def t_TOK_CH_EX(t):
	r'[(){}<>\[\]]'
	t.type = _ch_type_map[t.value]
	t.value = [t.value]
	return t

def t_error(t):
	end = t.value.find("\n")
	RaiseError("Unknown syntax!",">" + t.value[:end] + "")

def t_eof(t):
	return None

###########################################################################################################

g_lexer = lex.lex()

def StringTokenize(source_identifier,content, inherited_location, offset ):
	if(content == ""):
		return []

	global g_processed_source_name
	global g_current_line
	global _prep_map

	g_processed_source_name = source_identifier
	g_lexer.input(content)

	result = []

	g_current_line = 0
	g_lexer.lineno = 0

	while True:
		current_line = g_lexer.lineno
		tok_loc = [source_identifier,current_line + offset]
		tok = g_lexer.token()

		if not tok:
			break

		translated_tok = _prep_map.get(tok.type,None)
		if translated_tok == None:
			continue;

		(tok_tp,tok_flags) = translated_tok

		if tok_flags & _prep_flags.k_endl_flag:
			tok_loc.append(g_lexer.lineno - current_line)

		if inherited_location != None:
			tok_flags = tok_flags | _prep_flags.k_inherited_location
			tok_loc.append(inherited_location)

		result.append(( tok_flags, tok_tp, tok.value, tok_loc ))

	g_processed_source_name = None

	return result

###########################################################################################################

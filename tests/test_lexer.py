import precompiler.default
import precompiler
import precompiler._utils.pc_utils as _pc_utils

import unittest
import sys
import os



class TestLexer(unittest.TestCase):

	def check_token_integrity(self,tok,value_num,location_length):
		self.assertTrue(len(tok) == 4) #flags,type,value,location
		location = tok[3]
		value = tok[2]
		self.assertTrue(len(value) == value_num)
		self.assertTrue(len(location) == location_length)

	def check_one_token(self,check_string, expected_values, expected_location):
		lexer = precompiler.createLexer()
		tokens = lexer.StringTokenize("test_path",check_string,None,0)

		#print(">>>>>>>>>>",tokens)
		self.assertTrue(len(tokens) == 1)
		tok = tokens[0]
		self.check_token_integrity(tok,expected_values,expected_location);

		self.assertTrue(tok[2][0] == check_string)

		self.assertTrue(tok[3][0] == "test_path") #source file
		self.assertTrue(tok[3][1] == 0) #source line
		return tok


	def test_lexer_whitespace(self):
		tok = self.check_one_token(" ",1,2)
		self.assertTrue(tok[0] == _pc_utils.token_flags.k_trivial_flag)
		self.assertTrue(tok[1] == _pc_utils.primitive_tokens.kWhitespace)

	def test_newlines(self):
		tok = self.check_one_token("\n",1,3)
		self.assertTrue(tok[0] == _pc_utils.token_flags.k_trivial_flag | _pc_utils.token_flags.k_endl_flag)
		self.assertTrue(tok[1] == _pc_utils.primitive_tokens.kWhitespace)
		self.assertTrue(tok[3][2] == 1)

		tok = self.check_one_token("\n\n\n",1,3)
		self.assertTrue(tok[0] == _pc_utils.token_flags.k_trivial_flag | _pc_utils.token_flags.k_endl_flag)
		self.assertTrue(tok[1] == _pc_utils.primitive_tokens.kWhitespace)

		self.assertTrue(tok[3][2] == 3)

	def test_comment_line(self):
		tok = self.check_one_token("//comment",1,2)
		self.assertTrue(tok[0] == _pc_utils.token_flags.k_trivial_flag)
		self.assertTrue(tok[1] == _pc_utils.primitive_tokens.kComment)
		#self.assertTrue(tok[3][2] == 1)

	def test_comment_line_ex(self):
		tok = self.check_one_token("//comment\n",1,3)
		self.assertTrue(tok[0] == _pc_utils.token_flags.k_trivial_flag | _pc_utils.token_flags.k_endl_flag)
		self.assertTrue(tok[1] == _pc_utils.primitive_tokens.kComment)
		self.assertTrue(tok[3][2] == 1)

	def test_identifier(self):
		tok = self.check_one_token("abcASD",1,2)
		self.assertTrue(tok[0] == 0)
		self.assertTrue(tok[1] == _pc_utils.primitive_tokens.kIdentifier)

		tok = self.check_one_token("Aname123",1,2)
		self.assertTrue(tok[0] == 0)
		self.assertTrue(tok[1] == _pc_utils.primitive_tokens.kIdentifier)

		tok = self.check_one_token("name_Aname",1,2)
		self.assertTrue(tok[0] == 0)
		self.assertTrue(tok[1] == _pc_utils.primitive_tokens.kIdentifier)

		tok = self.check_one_token("_Xname",1,2)
		self.assertTrue(tok[0] == 0)
		self.assertTrue(tok[1] == _pc_utils.primitive_tokens.kIdentifier)

		tok = self.check_one_token("_",1,2)
		self.assertTrue(tok[0] == 0)
		self.assertTrue(tok[1] == _pc_utils.primitive_tokens.kIdentifier)
		tok = self.check_one_token("_123",1,2)
		self.assertTrue(tok[0] == 0)
		self.assertTrue(tok[1] == _pc_utils.primitive_tokens.kIdentifier)

	def test_file(self):
		lexer = precompiler.createLexer()
		fi = precompiler.createFileInterface(lexer)
		token = fi.GetFileTokens(os.environ["TEST_FILE"])
		self.assertTrue(True) #at this point we did not throw any exception

if __name__ == '__main__':
	unittest.main()
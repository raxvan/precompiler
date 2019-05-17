import precompiler.default
import precompiler
import precompiler._utils.pc_file_utils as _pc_file_utils
import unittest
import sys
import os

test_data = os.environ["API_TEST_FOLDER"]

def preprocess_and_test(file,ref_file,context_optione,output_options):
	lexer = precompiler.createLexer()
	fi = precompiler.createFileInterface(lexer)
	ctx = precompiler.createContext(fi,context_optione)
	input_file_path = os.path.join(test_data,file)

	ctx.AddInputFile(input_file_path)
	output_file_path = os.path.join(test_data,"_.tmp")
	ctx.SetOutputFile(output_file_path,output_options)
	ctx.Run()

	result_content = _pc_file_utils.open_and_read_textfile(output_file_path)
	refference_content = _pc_file_utils.open_and_read_textfile(os.path.join(test_data,ref_file))
	if result_content != refference_content:
		return False

	return True

class TestApi(unittest.TestCase):

	def test_no_options(self):
		self.assertTrue(preprocess_and_test("sample.txt","sample.ref",None,None)) 

	def test_no_comments(self):
		self.assertTrue(preprocess_and_test("sample.txt","sample_no_comments.ref",None,precompiler.OutOptions.remove_comments)) 

	def test_no_comments_and_newlines(self):
		self.assertTrue(preprocess_and_test("sample.txt","sample_no_comments_and_newlines.ref",None,precompiler.OutOptions.remove_comments | precompiler.OutOptions.collapse_endlines)) 

	def test_wminimized(self):
		self.assertTrue(preprocess_and_test("sample.txt","sample_wminimized.ref",None,precompiler.OutOptions.remove_comments | precompiler.OutOptions.collapse_whitespaces))

if __name__ == '__main__':
	unittest.main()
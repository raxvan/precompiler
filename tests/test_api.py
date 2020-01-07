import precompiler.default
import precompiler
import precompiler._utils.pc_file_utils as _pc_file_utils
import unittest
import sys
import os

test_data = os.environ["API_TEST_FOLDER"]

def create_context(file, context_option,output_options):
	lexer = precompiler.createLexer()
	fi = precompiler.createFileInterface(lexer)
	ctx = precompiler.createContext(fi,context_option)
	input_file_path = os.path.join(test_data,file)

	ctx.AddInputFile(input_file_path)
	output_file_path = os.path.join(test_data,file + ".tmp")
	ctx.SetOutputFile(output_file_path,output_options)

	return ctx

def compare_results(output_file,ref_file):
	output_file_path = os.path.join(test_data,output_file + ".tmp")
	result_content = _pc_file_utils.open_and_read_textfile(output_file_path)
	refference_content = _pc_file_utils.open_and_read_textfile(os.path.join(test_data,ref_file))
	if result_content != refference_content:
		return False

	return True

def preprocess_and_test(file,ref_file,context_option,output_options):
	ctx = create_context(file,context_option, output_options)
	ctx.Run()
	return compare_results(file,ref_file)

def test_LoadConfigFile(file,ref_file):
	ctx = create_context(file,None, None)
	ctx.LoadConfigFile(os.path.join(test_data,file))
	ctx.Run()
	return compare_results(file,ref_file)

def test_AddUserDefine(file,ref_file):
	ctx = create_context(file,None, None)
	ctx.AddUserDefine("CUSTOM_USER_DEFINE")
	ctx.AddUserDefineValue("CUSTOM_USER_DEFINE_WITH_VALUE","custom_value")
	ctx.Run()
	return compare_results(file,ref_file)

class TestApi(unittest.TestCase):

	def test_no_options(self):
		self.assertTrue(preprocess_and_test("sample.txt","sample_no_flags.ref",None,None))

	def test_no_comments(self):
		self.assertTrue(preprocess_and_test("sample.txt","sample_no_comments.ref",None,precompiler.OutOptions.remove_comments))

	def test_no_comments_and_newlines(self):
		self.assertTrue(preprocess_and_test("sample.txt","sample_no_comments_and_newlines.ref",None,precompiler.OutOptions.remove_comments | precompiler.OutOptions.collapse_endlines))

	def test_wminimized(self):
		self.assertTrue(preprocess_and_test("sample.txt","sample_wminimized.ref",None,precompiler.OutOptions.remove_comments | precompiler.OutOptions.collapse_whitespaces))

	def test_api_load_config_file(self):
		self.assertTrue(test_LoadConfigFile("config_test.ini","config_test.ref"))

	def test_api_add_user_define(self):
		self.assertTrue(test_AddUserDefine("user_define_test.txt","user_define_test.ref"))

if __name__ == '__main__':
	unittest.main()

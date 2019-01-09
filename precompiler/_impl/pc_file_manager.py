
import os
import re
import time
import hashlib

import precompiler
import precompiler._impl.pc_output as _impl_pc_output
import precompiler._utils.pc_utils as _pc_utils
import precompiler._utils.pc_file_utils as _pc_file_utils


class FileDataAdapter(object):
	def __init__(self,_name):
		self.name = _name
		self.content_sha512_str = None
		self.str_content = None
		self.tok_content = None
		self.tok_stash = None

	def stash(self):
		if self.tok_stash == None:
			self.tok_stash = self.tok_content
			self.tok_content = []

	def apply_stash(self):
		if self.tok_stash != None:
			self.tok_content = self.tok_stash
			self.tok_stash = None

	def tokens(self):
		return self.tok_content

	def hash(self):
		return self.content_sha512_str

	def hash_qeuals(self,input_hash):
		if self.content_sha512_str == input_hash:
			return True
		return False


###########################################################################################################

class DefaultFileManager(object):
	def __init__(self,lexer_interface):
		self.search_paths = []

		self.database = {}
		

		self.environ_regex = r"\{(?P<name>[a-zA-Z_]\w*)\}"
		self.local_environ = {}

		self.time_io_read = 0 #time spent in io load
		self.time_lexer = 0 #time spent in tokenizing stuff

		self.lexer_interface = lexer_interface

	def GetStats(self):
		return {
			"lexer_seconds" : self.time_lexer,
			"fread_seconds" : self.time_io_read,
		}

	def CreateAssembler(self,abs_file_path,flags):
		if (flags == None):
			flags = 0

		file_writer = self.CreateFileOutputHandler(abs_file_path)

		if (flags & (precompiler.OutOptions.colapse_endlines | precompiler.OutOptions.colapse_whitespaces | precompiler.OutOptions.try_whitespace_removal)) != 0:
			file_writer = _pc_utils.WhitespaceMinimizer(file_writer)

			if ( flags & precompiler.OutOptions.try_whitespace_removal ) != 0:
				file_writer.join_tokens = True
			if ( flags & precompiler.OutOptions.colapse_whitespaces ) != 0:
				file_writer.colapse_whitespaces = True
			if ( flags & precompiler.OutOptions.colapse_endlines ) != 0:
				file_writer.colapse_endlines = True

		if ( flags & precompiler.OutOptions.remove_commentes ) != 0:
			file_writer = _impl_pc_output.CommentRemoval(file_writer)

		return file_writer

	def CreateFileOutputHandler(self,abs_file_path):
		(path,filename) = os.path.split(abs_file_path)
		_pc_file_utils.make_paths(path)

		h = open(abs_file_path,"w")
		if h == None:
			onFailedToCreateFile(abs_file_path)

		return _pc_utils.BufferedFileAssembler(h,abs_file_path,128)

	def GetOrLoadFile(self,abs_file_path):
		fh = self.database.get(abs_file_path,None)
		if fh != None:
			return fh

		handle = FileDataAdapter(abs_file_path)

		(handle.str_content,handle.content_sha512_str) = self._load_file_str(abs_file_path)
		handle.tok_content = self._load_tok_from_str(abs_file_path,handle.str_content)

		self.database[abs_file_path] = handle

		return handle

	def CreateOutputComment(self,message):
		return self.lexer_interface.CreateLineCommentFromText(message)

	def _load_file_str(self,abs_file_path):
		start_time = time.time()
		file_content = _pc_file_utils.open_and_read_textfile(abs_file_path)
		if file_content == None:
			file_content = self.onFailedToLoadFile(abs_file_path)
		content_hash = hashlib.sha512(file_content.encode()).hexdigest() 
		end_time = time.time()

		self.time_io_read += (end_time - start_time)

		return (file_content,content_hash)

	def _load_tok_from_str(self,abs_file_path,str_content):
		start_time = time.time()
		tokens = self.lexer_interface.StringTokenize(abs_file_path,str_content,None)
		end_time = time.time()

		self.time_lexer += (end_time - start_time)

		return tokens

	def GetFileTokens(self,abs_file_path):
		file_handle = self.GetOrLoadFile(abs_file_path)
		return file_handle.tok_content

	def RetokenizeContent(self,content_str, inherited_token):
		file = _pc_utils.TokSource(inherited_token)[0]
		return self.lexer_interface.StringTokenize(file,content_str,inherited_token)

	def FormatPathIdentifier(self,name):
		env_value = self.local_environ.get(name,None)
		if env_value != None:
			return env_value

		env_value = os.environ.get(name,None)
		if env_value != None:
			return env_value
		return None

	def _replace_path_re(self,rematch):
		name = rematch.group('name')
		return self.FormatPathIdentifier(name);

	def FormatUserPath(self,str_value):
		result = re.sub(self.environ_regex, lambda a: self._replace_path_re(a), str_value)
		return os.path.normpath(result)

	def _find_formatting_arguments(matchre):
		name = matchre.group('name')
		result = self.FormatPathIdentifier(name)
		if result != None:
			return result
		return "{None:" + name + "}"

	def LocateFile(self,nrm_path,local_dir):
		if os.path.exists(nrm_path):
			return os.path.normpath(os.path.abspath(nrm_path))

		lpath = os.path.normpath(os.path.join(local_dir,nrm_path))
		if os.path.exists(lpath):
			return os.path.abspath(lpath)

		for p in self.search_paths:
			test = os.path.normpath(os.path.join(local_dir,nrm_path))
			if os.path.exists(test):
				return os.path.abspath(nrm_path)

	#return abs file path
	def FindFileWithPath(self,user_raw_path,current_unit):
		formated_path = self.FormatUserPath(user_raw_path)
		(current_root,_fulename) = os.path.split(current_unit)
		return self.LocateFile(formated_path,current_root)

	def StashFileContent(self,abs_file_path):
		fh = self.database.get(abs_file_path,None)
		assert fh != None, "Internal Error; The file stash should already have the file loaded"
		fh.stash()
		
	def RevertStash(self,abs_file_path):
		fh = self.database.get(abs_file_path,None)
		assert fh != None, "Internal Error; The file stash should already have the file loaded"
		fh.apply_stash()

	def ResetFileSystem(self,reset_stats):
		for k,v in self.database.items():
			v.apply_stash()
		if reset_stats:
			self.time_io_read = 0
			self.time_lexer = 0

	def onFailedToLoadFile(self,abs_file_path):
		raise Exception("Failed to load file [" + abs_file_path + "]!")

	def onFailedToCreateFile(self,abs_dest_path):
		raise Exception("Failed to create file [" + abs_dest_path + "]!")



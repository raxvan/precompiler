
import os
import re
import time

import precompiler
import precompiler._impl.pc_output as _impl_pc_output
import precompiler._utils.pc_utils as _pc_utils
import precompiler._utils.pc_file_utils as _pc_file_utils

###########################################################################################################

class DefaultFileManager(object):
	def __init__(self,lexer_interface):
		self.search_paths = []

		self.file_str_cache = {}
		self.file_tok_cache = {}

		self.unique_stash = {}

		self.environ_regex = re.compile("\{(?P<name>[a-zA-Z_]\w*)\}")
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

	def GetFileStr(self,abs_file_path):

		cached_str = self.file_str_cache.get(abs_file_path,None)
		if cached_str != None:
			return cached_str

		start_time = time.time()
		tf = _pc_file_utils.open_and_read_textfile(abs_file_path)
		if tf == None:
			tf = self.onFailedToLoadFile(abs_file_path)
		end_time = time.time()
		self.file_str_cache[abs_file_path] = tf
		self.time_io_read += (end_time - start_time)

		return tf

	def GetFileTokens(self,abs_file_path):

		cache_content = self.file_tok_cache.get(abs_file_path,None)

		if cache_content != None:
			return cache_content

		file_str = self.GetFileStr(abs_file_path)

		start_time = time.time()
		tokens = self.lexer_interface.StringTokenize(abs_file_path,file_str,None,0)
		end_time = time.time()

		self.file_tok_cache[abs_file_path] = tokens
		self.time_lexer += (end_time - start_time)

		return tokens


	def RetokenizeContent(self,content_str, inherited_location):
		file = inherited_location[0]
		offset = inherited_location[1]
		return self.lexer_interface.StringTokenize(file,content_str,None,offset)

	def FormatPathIdentifier(self,name):
		env_value = os.environ.get(name.upper(),None)
		if env_value != None:
			return env_value

		env_value = argument_map.get(name.lower(),None)
		if env_value != None:
			return env_value

		env_value = os.environ.get(name,None)
		if env_value != None:
			return env_value
		return None

	def FormatUserPath(self,str_value):
		result = re.sub(self.environ_regex, lambda a: self._replace_match(a), str_value)
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
		if self.unique_stash.get(abs_file_path,None) != None:
			return
		#save file content for later use
		self.unique_stash[abs_file_path] = self.file_tok_cache[abs_file_path]
		#make content "empty"
		self.file_tok_cache[abs_file_path] = []

	def RevertStash(self,abs_file_path):
		stash = self.unique_stash.get(abs_file_path,None)
		if stash != None:
			self.file_tok_cache[abs_file_path] = stash
			self.unique_stash[abs_file_path] = None

	def ResetFileSystem(self):
		self.file_tok_cache.update(self.unique_stash)
		self.unique_stash = {}

	def onFailedToLoadFile(self,abs_file_path):
		raise Exception("Failed to load file [" + abs_file_path + "]!")

	def onFailedToCreateFile(self,abs_dest_path):
		raise Exception("Failed to create file [" + abs_dest_path + "]!")



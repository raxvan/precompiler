
import os

#open and read all file contents; None is returned if file can't be opened
def open_and_read_textfile(file_path):
	fo = open(file_path, 'r',encoding='utf-8')
	if fo:
		content = fo.read()
		fo.close()
		return content
	return None


def make_paths(abs_path):
	if not os.path.exists(abs_path):
		os.makedirs(abs_path)
# -*- coding: utf-8 -*-

from construct import *
import sys
from pathlib import Path

SDATStruct = Struct(
    'magic'/Const(b'Filename'),
    'file_header'/Struct(
        'unk1'/Int32ul,
        'pack_header_offset'/Int32ul,
        'pack_header_align'/Computed(lambda this: 8 - this.pack_header_offset % 8 if this.pack_header_offset % 8 != 0 else 0)
    ),
    'pack_header'/Pointer(
        this.file_header.pack_header_offset, Struct(
            'pack_header_padding'/Padding(this._root.file_header.pack_header_align),
            'pack_sign'/Const(b'Pack'),
            'unk1'/Int32ul,
            'unk2'/Int32ul,
            'pack_header_length'/Int32ul,
            'file_cnt'/Int32ul,
            'file_entries'/Array(
                this.file_cnt, Struct(
                    'index'/Index,
                    'file_data_offset'/Int32ul,
                    'file_size'/Int32ul,
                    'file_data'/Pointer(this.file_data_offset, Bytes(this.file_size))
                )
            )
        )
    ),
    'file_name_offsets'/Array(this._root.pack_header.file_cnt, Int32ul),
    'file_names'/Array(this._root.pack_header.file_cnt, CString('UTF-8'))
)


def unpack_sdat(sdat_file, ex_dir):
    st = SDATStruct.parse_file(sdat_file)
    for file_name, file_entry in zip(st.file_names, st.pack_header.file_entries):
        file_path = ex_dir/file_name
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True)
        with open(file_path, 'wb') as f:
            f.write(file_entry.file_data)
        print(f'{file_path} saved!')


if __name__ == '__main__':
    budle_folder = Path(sys.argv[0]).parent
    try:
        sdat_file = Path(sys.argv[1])
    except:
        input('输入路径错误！')
        sys.exit()
    ex_dir = budle_folder/sdat_file.stem
    unpack_sdat(sdat_file, ex_dir)
    input('拆包完成!')

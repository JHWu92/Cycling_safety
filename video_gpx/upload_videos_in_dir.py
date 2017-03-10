# coding=utf-8
import subprocess
import glob
import argparse
import os


def main(args):
    directory = args.input_directory
    result_file = os.path.join(directory + 'upload_result.tsv')
    if not os.path.exists(result_file):
        with open(result_file, 'w') as f:
            f.write('uploaded\tfile_name\tvfile\tclip_id\turl\n')

    for path in glob.glob(os.path.join(directory, 'DCIM/*/*.MP4')):
        path = path.replace('\\', '/')
        clip_path = path.replace(directory, '')
        top_folder, sub_folder, clip_fn = clip_path.split("/")
        clip_fn = clip_fn[:-4]
        vfile, cid = clip_fn.split('_')
        vfile = '{}/{}/{}.MP4'.format(top_folder, sub_folder, vfile)
        title = '{}/{}'.format(sub_folder, clip_fn)

        print 'uploading file: %s...' % path
        cmd = r'python upload_video.py --file "{path}" --title {title} --clipID {cid} --vfile {vfile} --resultFile {result_file}'.format(
            path=path, title=title, cid=cid, vfile=vfile, result_file=result_file)
        # subprocess.call(cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='upload videos clips in the input directory')
    parser.add_argument('-i', '--input-directory', help='the input directory of videos clips', type=str)
    # directory = r"Sample Data/test_upload_videos_in_dir/"
    args = parser.parse_args()

    main(args)

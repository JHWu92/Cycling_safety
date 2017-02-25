# coding=utf-8


def main():
    # LOGGER.info('test')
    return


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='visualize raw gpx and snapped traces')
    parser.add_argument('-i', '--input-directory', type=str, help='directory of raw gpx trace')
    parser.add_argument('-s', '--snapped-directory', type=str, help='directory of snapped gpx trace', default='split')
    
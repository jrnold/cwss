#!/usr/bin/env python
""" Sync local CWSS data with data stored in AWS S3
"""
import argparse
import subprocess as sp

DST = 'data'
S3_BUCKET = 'jrnold-nps-cwss'
REGION = 'us-east-1'

def upload(args):
    sp.run(['aws', 's3', 'sync', '--delete', '--region', args.region, args.dst, 's3://%s' % args.bucket])
    pass

def download(args):
    sp.run(['aws', 's3', 'sync', '--delete',  '--region', args.region, 's3://%s' % args.bucket, args.dst])
    pass

def main():
    parser = argparse.ArgumentParser(description='Upload to or download data CWSS data from AWS.')
    parser.add_argument('--region', dest='region', nargs=1, default = REGION)
    parser.add_argument('--bucket', dest='bucket', nargs=1, default = S3_BUCKET)
    parser.add_argument('--dst', dest='dst', nargs=1, default = DST)
    parser.set_defaults(func=download)
    subparsers = parser.add_subparsers(help='additional help', title='subcommands', description = 'valid subcommands')
    parser_upload = subparsers.add_parser('upload')
    parser_upload.set_defaults(func = upload)
    parser_download = subparsers.add_parser('download')
    parser_download.set_defaults(func = download)
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

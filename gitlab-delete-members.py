#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""Handy script for searching and deleting members from Gitlab projects.

Built on top of GitLab Python API: https://python-gitlab.readthedocs.io/
"""

import argparse

import gitlab


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Delete member from all accessible gitlab projects.')
    parser.add_argument('--query', required=True,
                        help='Gitlab query string that defines users '
                        'to be deleted (username is recommended)')
    parser.add_argument('--token', required=True,
                        help='Gitlab token of your user')
    parser.add_argument('--url', default='https://gitlab.com',
                        help='Gitlab URL')
    parser.add_argument('--visibility', default='private',
                        help='Gitlab projects visibility')
    parser.add_argument('--dry', action='store_true',
                        help='dry run')
    return parser.parse_args()


def print_ok():
    """Print fancy ok message."""
    print('🟢 ok')


def print_fail():
    """Print fancy fail message."""
    print('🔴 fail')


def print_skip():
    """Print fancy skip message."""
    print('🟡 skip')


def main():
    """Script entry point."""
    # Greeting and args parsing.
    args = parse_args()

    # Initialize Gitlab API.
    print(f'💬 Auth to {args.url} : ', end='')
    gl = gitlab.Gitlab(args.url, private_token=args.token)
    try:
        gl.auth()
        print_ok()
    except:  # noqa
        print_fail()
        return

    # Iterate over projects.
    projects = gl.projects.list(all=True, visibility=args.visibility)
    del_members_count = 0
    del_projects_count = 0
    for p in projects:
        print(f'Project "{p.name_with_namespace}" (id={p.id}) :',
              end='')

        # Query members.
        members = p.members.list(query=args.query)

        # Delete members.
        if len(members) == 0:
            print(' no users to delete')
        else:
            del_projects_count += 1
            for m in members:
                print(f' delete {m.username} (id={m.id}) : ', end='')
                if not args.dry:
                    try:
                        m.delete()
                        print_ok()
                        del_members_count += 1
                    except:  # noqa
                        print_fail()
                else:
                    print_skip()

    # Statistics.
    print(f'💬 {del_members_count} members deleted '
          f'in {del_projects_count} repositories')


if __name__ == '__main__':
    main()

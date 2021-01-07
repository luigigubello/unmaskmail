import click
import os
import sys
import json


# https://github.com/pallets/click/issues/886
def print_help(ctx, value):
    if value is False:
        return
    click.echo(ctx.get_help())
    ctx.exit()


alpha_dict = {}
len_dict = {}

# https://gist.githubusercontent.com/tbrianjones/5992856/raw/93213efb652749e226e69884d6c048e595c1280a/free_email_provider_domains.txt
path_file = 'list.txt'


def create_dicts(path_file):
    if not os.path.isfile(path_file):
        error = {"error": "file not exist or not accessible"}
        print("Error: {}".format(error['error']))
        sys.exit(1)
    # https://stackoverflow.com/questions/17039457/convert-first-column-of-data-from-text-file-into-a-list-in-python
    with open(path_file) as f:
        lis = []
        for line in f:
            spl = line.split()
            lis.append(spl[0])
    if not lis:
        error = {"error": "empty file"}
        print("Error: {}".format(error['error']))
        sys.exit(1)
    else:
        alpha_d = {}
        len_d = {}
        for item in lis:
            if item[0] not in alpha_d:
                alpha_d[item[0]] = []
                alpha_d[item[0]].append(item)
            else:
                alpha_d[item[0]].append(item)
            n = len(item.split(".", 1)[0])
            if n not in len_d:
                len_d[n] = []
                len_d[n].append(item)
            else:
                len_d[n].append(item)
    return [alpha_d, len_d]


@click.command()
@click.option('--head', '-h', type=str, help='First letter(s) of the second-level domain.')
@click.option('--length', '-l', type=int, help='Length of the second-level domain.')
@click.option('--tld', type=str, help='Top-level domain.')
@click.option('--json', 'json_dict', is_flag=True, help='Print result in json format.')
@click.option('--help', is_flag=True, expose_value=False, is_eager=False, callback=print_help,
              help="Print help message.")
@click.pass_context
def uncover_mail_run(ctx, head, length, tld, json_dict):
    """
    📧 Unmask e-mail address\n
    https://github.com/luigigubello/unmaskmail
    """
    error = {"error": "No domains found."}
    dicts = create_dicts(path_file)
    alpha_dict = dicts[0]
    len_dict = dicts[1]
    if not head and not length and not tld:
        print_help(ctx, value=True)
    final_list = []
    head_list = []
    if head:
        if not head.isalnum():
            error = {"error": "head need to be alphanumeric"}
            if not json_dict:
                print("Error: {}".format(error['error']))
            else:
                print(json.dumps(error))
            sys.exit(1)
        if len(head) == 1:
            head_list = alpha_dict[head]
        else:
            k = len(head)
            if head[0] in alpha_dict:
                for item in alpha_dict[head[0]]:
                    if len(item) >= k and item[:k] == head:
                        head_list.append(item)
            else:
                if not json_dict:
                    print("Error: {}".format(error['error']))
                else:
                    print(json.dumps(error))
                sys.exit(1)
    if length:
        if length < len(head):
            error = {"error": "length too short"}
            if not json_dict:
                print("Error: {}".format(error['error']))
            else:
                print(json.dumps(error))
            sys.exit(1)
        if length in len_dict:
            if head_list:
                head_list = list(set(head_list) & set(len_dict[length]))
        else:
            if not json_dict:
                print("Error: {}".format(error['error']))
            else:
                print(json.dumps(error))
            sys.exit(1)
    if tld and not head and not length:
        error = {"error": "--tld requires --head or --length"}
        if not json_dict:
            print("Error: {}".format(error['error']))
        else:
            print(json.dumps(error))
        sys.exit(1)
    else:
        if tld:
            for item in head_list:
                if item.split(".", 1)[1] == tld:
                    final_list.append(item)
        else:
            final_list = head_list
    if not final_list:
        if not json_dict:
            print("Error: {}".format(error['error']))
        else:
            print(json.dumps(error))
    else:
        if not json_dict:
            print("Possible domains:")
            i = 1
            for item in final_list:
                print("{}) {}".format(i, item))
                i += 1
        else:
            result = {"result": final_list}
            print(json.dumps(result))


if __name__ == '__main__':
    uncover_mail_run()

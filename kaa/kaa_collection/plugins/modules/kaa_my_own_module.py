#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: kaa_my_own_module

short_description: This is test_module for creating a file with a specific content   

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: Module create file along path using variables $path + $name 
and write to the file content form variable $content

options:
    path:
        description: This is the message to send to the test module.
        required: true
        type: str
    name:
        description: This is the message to send to the test module.
        required: true
        type: str
    content:
        description: This is content of file, which we want creat
        required: true
        type: str    

# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name

author:
    - Andrey Krylov (syatihoko@mail.ru)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  kaa_my_namespace.kaa_my_collection.kaa_my_own_module:
    name: 'file_name.txt'
    path: /tmp/folder_name/
    content: 'My Content for file'

# fail the module
- name: Test failure of the module
  kaa_my_namespace.kaa_my_collection.kaa_my_own_module:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule

#Добавили импорт os, to_bytes, to_text
import os, shutil
from ansible.module_utils._text import to_bytes
from ansible.module_utils._text import to_text


def run_module():
    # define available arguments/parameters a user can pass to the module
    #Аргументы модуля
    # module_args = dict(
    #     name=dict(type='str', required=True),
    #     new=dict(type='bool', required=False, default=False)
    # )
    module_args = dict(
        name=dict(type='str', required=True),  #Название файла
        path=dict(type='str', required=True),  #Путь к директори
        content=dict(type='str', required=True)  # Содержимое файла
    ) #что будет делать, создаст директори, в ней файл и наполнит его заготовленной информацией.


    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task

    result = dict(
        changed=False,  #Task в Ansible будет отображаться как Ok,
        #Если бы была True, то отображалась как Changed.
        original_message='',  #Полная версия того что вывелось
        message=''   #Например краткая версия того. что вывелось
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(    #Создаем экземпляр класса AnsibleModule
        argument_spec=module_args,
        supports_check_mode=True  #Поддерживается check
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode: #Если запускаем в check mode, то он выходит, как будто что то сделал
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    # Переопределяем параметры
    result['original_message'] = module.params['name']
    result['message'] = 'goodbye'

    file_path = os.path.join(to_bytes(module.params['path']) + to_bytes(module.params['name']))
    folder_path = module.params['path']
    temp_file_path = os.path.join(to_bytes('/tmp/') + to_bytes(module.params['name']))

    try:
    # #Изначально в байтах пришло, поэтому более не конвертируем. Так как отправлять мы тоже в байтах должны
        if os.path.exists(folder_path):  #если директория существует
            result['changed'] = False
            result['message'] = "Folder " + to_text(folder_path) + " already exist"
            # не использую f', чтобы сохранить совместимости с Python2
            result['original_message'] = result['message']
        else:  #если директории нет, то создаем
            result['message'] = "Create folder" + to_text(folder_path)
            result['original_message'] = result['message']
            os.makedirs(folder_path, mode=0o755, exist_ok=False)
            # exist_ok=False - если директория существует, то это не OK => except.
    except: result['original_message'] += 'Error while:  ' + result['message']



    #if not os.path.isfile(file_path):
    #Проверяем, что файл не существует os.F_OK - проверка сущ. объекта
    if (not os.access((temp_file_path), os.F_OK)):
        f = open(temp_file_path, 'wb')
        f.write(to_bytes(module.params['content']))  #текст который записываем в файл
        f.close()

    #Если нет целевого файла
    if (not os.access((file_path), os.F_OK)):
        shutil.copy(temp_file_path,file_path)
        os.remove(temp_file_path)
        result['changed'] = True
        result['message'] = "File " + to_text(file_path) + " create successful"
        result['original_message'] += '; ' + result['message']
    else:
        result['changed'] = False
        result['message'] = "File " + to_text(file_path) + " already exist"
        result['original_message'] += '; ' + result['message']

    result['message'] = to_bytes(result['message'])
    result['original_message'] = to_bytes(result['original_message'])

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    # if module.params['new']:
    #     result['changed'] = True
    #если параметр new будет, то changed = True, иначе будет Ok

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['name'] == 'fail me':  #для эксеперемнов с неправильным выходом,
        # например когда какой то реквест отвалился
        module.fail_json(msg='You requested this to fail', **result)
        # В сообщение пишем, что хотим добавляя все из словаря **result

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module() #запускаем вышенаписанную функцию, так сделанно чтобы можно было  запускать
    # несколько отдельных функций


if __name__ == '__main__':
    main()

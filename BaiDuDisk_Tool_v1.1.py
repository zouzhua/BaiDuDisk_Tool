import requests
from PIL import Image
from io import BytesIO
import re


class BaiDuDisk(object):
    def __init__(self, url):
        self.url_disk = url
        self.url_verify = 'https://pan.baidu.com/api/getvcode?prod=pan&channel=chunlei&web=1&app_id=250528&clienttype=0'
        self.url_download = ''
        self.vcode = ''
        self.file_data = {}
        self.data = {
            'encrypt': '0',
            'product': 'share',
            'uk': '3993209745',
            'primaryid': '',
            'fid_list': '',
            'path_list': '',
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
        }
        self.session = requests.session()
        self.__get_download_url()

    def __get_download_url(self):
        response = self.session.get(url=self.url_disk, headers=self.headers).content.decode('utf-8')
        response = re.findall('yunData.setData\({(.*?)}\)', response, re.S)[0]
        # 获取POST地址
        sign = re.findall('"sign":"(.*?)"', response, re.S)[0]
        timestamp = re.findall('"timestamp":(.*?),', response, re.S)[0]
        bdstoken = re.findall('"bdstoken":"(.*?)"', response, re.S)
        try:
            bdstoken = bdstoken[0]
        except IndexError:
            bdstoken = 'null'
        self.url_download = 'https://pan.baidu.com/api/sharedownload?sign=' + sign + '&timestamp=' + timestamp + '&channel=chunlei&web=1&app_id=250528&bdstoken=' + bdstoken + '&clienttype=0'
        # 获取data
        self.data['primaryid'] = re.findall('"shareid":(.*?),', response, re.S)[0]
        self.data['fid_list'] = '[' + re.findall('"fs_id":(.*?),', response, re.S)[0] + ']'

    def __show_verify_pic(self, url_picture):
        verify = self.session.get(url=url_picture, headers=self.headers).content
        im = Image.open(BytesIO(verify))
        im.show()

    def __show_result(self):
        unit = ['B', 'KB', 'MB', 'GB']
        size = self.file_data['filesize']
        p = 0
        while size > 1024:
            size /= 1024
            p += 1
        print('├文件名称:' + self.file_data['filename'])
        print('├文件大小:', size, unit[p], '(', self.file_data['filesize'], 'Byte)')
        print('├文件路径:' + self.file_data['path'])
        print('├路径MD5:' + self.file_data['path_md5'])
        print('├文件链接:' + self.file_data['dlink'])
        print('└文件MD5:' + self.file_data['md5'])

    def get_download(self):
        response = self.session.post(url=self.url_download, headers=self.headers, data=self.data).json()
        errno = response['errno']
        if errno != 0:
            print('<-需要输入验证码->')
            res = self.session.get(url=self.url_verify, headers=self.headers).json()
            self.vcode = res['vcode']
            url_verify_pic = res['img']
            self.__show_verify_pic(url_verify_pic)
            data = {
                'encrypt': '0',
                'product': 'share',
                'vcode_input': input('请输入验证码:'),
                'vcode_str': self.vcode,
                'uk': '3993209745',
                'primaryid': self.data['primaryid'],
                'fid_list': self.data['fid_list'],
                'path_list': ''
            }
            response = self.session.post(url=self.url_download, headers=self.headers, data=data).json()
            errno = response['errno']
            while errno != 0:
                url_verify_pic = self.session.get(url=self.url_verify, headers=self.headers).json()['img']
                self.__show_verify_pic(url_verify_pic)
                data['vcode_input'] = input('输入的验证码错位!请输入新的验证码:')
                response = self.session.post(url=self.url_download, headers=self.headers, data=data).json()
                errno = response['errno']
        print('<-操作完成->')
        response = response['list'][0]
        self.file_data = {
            'filename': response['server_filename'],
            'filesize': response['size'],
            'path_md5': response['path_md5'],
            'path': response['path'],
            'md5': response['md5'],
            'dlink': response['dlink'],
        }
        self.__show_result()


if __name__ == '__main__':
    newBaiduDisk = BaiDuDisk(input('请输入百度网盘地址:'))
    newBaiduDisk.get_download()

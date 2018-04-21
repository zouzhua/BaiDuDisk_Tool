import requests
import re


class BaiDuDisk(object):
    def __init__(self, url):
        self.disk_url = url
        self.download_url = ''
        self.vcode = ''
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
        }
        self.data = {
            'encrypt': '0',
            'product': 'share',
            'uk': '3993209745',
            'primaryid': '',
            'fid_list': '',
            'path_list': '',
        }
        self.session = requests.session()

    def get_download_url(self):
        response = self.session.get(url=self.disk_url, headers=self.headers).content.decode('utf-8')
        response = re.findall('yunData.setData\({(.*?)}\)', response, re.S)[0]
        # 获取POST地址
        sign = re.findall('"sign":"(.*?)"', response, re.S)[0]
        timestamp = re.findall('"timestamp":(.*?),', response, re.S)[0]
        bdstoken = re.findall('"bdstoken":"(.*?)"', response, re.S)
        if bdstoken == []:
            bdstoken = 'null'
        else:
            bdstoken = bdstoken[0]
        # 获取data
        self.data['primaryid'] = re.findall('"shareid":(.*?),', response, re.S)[0]
        self.data['fid_list'] = '[' + re.findall('"fs_id":(.*?),', response, re.S)[0] + ']'
        self.download_url = 'https://pan.baidu.com/api/sharedownload?sign=' + sign + '&timestamp=' + timestamp + '&channel=chunlei&web=1&app_id=250528&bdstoken=' + bdstoken + '&clienttype=0'

    def get_verify_picture(self):
        # 可以优化，无需每次都对验证码的地址进行获取
        url_get = 'https://pan.baidu.com/api/getvcode?prod=pan&t=0.038248671222508746&channel=chunlei&web=1&app_id=250528&bdstoken=null&logid=MTUyNDMxODg2MTgzMDAuMTk5NDI0MDY4NzA5MTAzMzQ=&clienttype=0'
        response = self.session.get(url=url_get, headers=self.headers).content.decode('utf-8')
        self.vcode = re.findall('"vcode":"(.*?)"', response, re.S)[0]
        url_picture = re.findall('"img":"(.*?)"', response, re.S)[0].replace('\\', '')
        verify = self.session.get(url=url_picture, headers=self.headers).content
        with open('D:\\verify.jpg', 'wb') as f:
            f.write(verify)

    def get_download(self):
        response = self.session.post(url=self.download_url, headers=self.headers, data=self.data).content.decode(
            'utf-8')
        error = re.findall('"errno":(.*?),', response, re.S)[0]
        print(response)
        if error == '0':
            # 无需验证码
            pass
        else:
            print('请输入验证码:', end='')
            self.get_verify_picture()
            data = {
                'encrypt': '0',
                'product': 'share',
                'vcode_input': input(),
                'vcode_str': self.vcode,
                'uk': '3993209745',
                'primaryid': self.data['primaryid'],
                'fid_list': self.data['fid_list'],
                'path_list': ''
            }
            response = self.session.post(url=self.download_url, headers=self.headers, data=data).content.decode('gbk')
            errno = re.findall('"errno":(.*?),', response)[0]
            while errno != '0':  # 如果errno不为0，则说明验证码不正确，要再次输入
                print('输入的验证码错位!请输入新的验证码:', end='')
                self.get_verify_picture()
                data = {
                    'encrypt': '0',
                    'product': 'share',
                    'vcode_input': input(),
                    'vcode_str': self.vcode,
                    'uk': '3993209745',
                    'primaryid': self.data['primaryid'],
                    'fid_list': self.data['fid_list'],
                    'path_list': ''
                }
                response = self.session.post(url=self.download_url, headers=self.headers, data=data).content.decode(
                    'gbk')
                errno = re.findall('"errno":(.*?),', response)[0]
            # 正确时
            dlink = re.findall('"dlink":"(.*?)"', response, re.S)[0].replace('\\', '').encode('utf-8').decode('utf-8')
            path = re.findall('"path":"(.*?)"', response, re.S)[0].encode('utf-8').decode('unicode_escape').replace(
                '\\', '')
            print(dlink)
            print(path)


if __name__ == '__main__':
    newBaiduDisk = BaiDuDisk('https://pan.baidu.com/s/1hsuPymw')
    newBaiduDisk.get_download_url()
    newBaiduDisk.get_download()

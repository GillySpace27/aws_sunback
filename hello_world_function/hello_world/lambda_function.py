import requests
from datetime import datetime
from bs4 import BeautifulSoup
from astropy.io import fits
from tqdm import tqdm
from modify import Modify
import boto3
s3 = boto3.resource('s3')
bucket = s3.Bucket('gillyspace27-test-billboard')
s3_client = boto3.client('s3')


# import pdb; pdb.set_trace()
# SITE = os.environ['site']  # URL of the site to check, stored in the site environment variable
# EXPECTED = os.environ['expected']  # String expected to be on the page, stored in the expected environment variable
SITE = "http://jsoc2.stanford.edu/data/aia/synoptic/mostrecent/"
archive_url = "http://jsoc2.stanford.edu/data/aia/synoptic/mostrecent/"
save_path = "fits/"


def lambda_handler(event=None, context=None):
    """is called by aws"""

    try:
        img_links = get_img_links()
        modify_img_series(img_links)
    except:
        print('Check failed!')
        raise
    else:
        print('Check passed!')
    finally:
        print('Check complete at {}'.format(str(datetime.now())))

def get_img_links():
    """gets the list of files to pull"""
    # create response object
    r = requests.get(archive_url)

    # create beautiful-soup object
    soup = BeautifulSoup(r.content, 'html5lib')

    # find all links on web-page
    links = soup.findAll('a')

    # filter the link sending with .mp4
    img_links = [archive_url + link['href'] for link in links if link['href'].endswith('fits')]

    return img_links

def modify_img_series(img_links):
    """downloads the images"""
    imgs = []
    print("Downloading Images", flush=True)
    for link in tqdm(img_links):
        # print(link)
        with fits.open(link) as hdul:
            imgs.extend(modify_img(hdul))
    upload_imgs(imgs)

def modify_img(hdul):
    hdul.verify('silentfix+warn')

    wave = hdul[0].header['WAVELNTH']
    t_rec = hdul[0].header['T_OBS']
    data = hdul[0].data
    image_meta = str(wave), str(wave), t_rec, data.shape
    mod_obj = Modify(data, image_meta)
    return mod_obj.get_paths()

def upload_imgs(imgs):
    print("Uploading Images", flush=True)

    for img in tqdm(imgs):
        bucket.upload_file(img, 'album1/' + img.split('/')[-1], ExtraArgs={'ACL':'public-read', "ContentType":"image/png"})

if __name__ == "__main__":
    # Do something if this file is invoked on its own
    lambda_handler()

# fitFile =

#     print(link)
#
#     '''iterate through all links in img_links
#     and download them one by one'''
#
#     # obtain filename by splitting url and getting
#     # last string
#     file_name = link.split('/')[-1]
#
#     # print("Downloading file:%s"%file_name)
#
#     # create response object
#     resp = requests.get(link, stream=True)
#     resp.raw.decode_content = True
#     img = resp.raw
#     import pdb; pdb.set_trace()
#
#     # # download started
#     # # os.makedirs(save_path, exist_ok=True)
#     # with open(save_path+file_name, 'wb') as f:
#     #     for chunk in r.iter_content(chunk_size = 1024*1024):
#     #         if chunk:
#     #             f.write(chunk)
#
#     # print("%s downloaded!\n"%file_name)
#
# print("All imgs downloaded!")
# return


    # imgs = mod_obj.get_imgs()
    #
    # import matplotlib.pyplot as plt
    # fig, ax = plt.subplots()
    # # Image from plot
    # ax.axis('off')
    # fig.patch.set_facecolor('k')
    # fig.tight_layout(pad=0)
    # fig.set_size_inches((10,10))
    # ax.margins(-0.49)
    #
    # ax.imshow(imgs[1], interpolation='quadric')
    # plt.show()

    # print(imgs)

# def export(figbox, image_meta):
#     full_name, save_path, time_string, shape = image_meta
#     pixels = shape[0]
#     dpi = pixels / 10
#     try:
#         for fig, processed in figbox:
#
#             middle = '' if processed else "_orig"
#
#             new_path = save_path[:-5] + middle + ".png"
#             # name = self.clean_name_string(full_name)
#             directory = "renders/"
#             path = directory + new_path.rsplit('/')[1]
#             # os.makedirs(directory, exist_ok=True)
#             # self.newPath = path
#             fig.savefig(path, facecolor='black', edgecolor='black', dpi=dpi)
#             # plt.close(fig)
#             print("\tSaved {} Image:{}".format('Processed' if processed else "Unprocessed", full_name))
#
#     except Exception as e:
#         raise e
#     finally:
#         for fig, processed in figbox:
#             plt.close(fig)
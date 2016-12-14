import requests
import json
from bs4 import BeautifulSoup

#time in unix format
import time


def crawl_info_based_on_time(start_time, end_time, outputfilepath):

    headers = {
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'en-US,en;q=0.8',
        'cookie': 'xb=168666; BX=9vkmdfpc51d7m&b=3&s=hh; flrbrgs=1; RT=s=1481688457562&u=&r=https%3A//www.flickr.com/search/min_taken_date%3D1480568400%26max_taken_date%3D1480741199%26sort%3Ddate-posted-desc; _gat=1; current_identity=1-1481671282; ffs=145765593-29; cookie_session=145765593%3Ad1a1505cae4d10a8e58613718d5da69a; cookie_accid=145765593; cookie_epass=d1a1505cae4d10a8e58613718d5da69a; sa=1486873657%3A145786923%40N07%3A0074a045c0a3cd78c6c14cd8f62acd52; localization=en-us%3Bus%3Bus; flrbp=1481689657-341e97b6d8c583d0c4a31cd1e24750ee8be9df55; flrbs=1481689657-e310c6740e75a290bd9a038f120c57ae5fdf9e6a; flrbgrp=1481689657-4025d939541e85644dc647bce548aa37f201b55d; flrbgdrp=1481689657-26cb50576351ae17af09500daa299c6cc8a3bca2; flrbgmrp=1481689657-ec6fb6f951416d89f381f1ae1151c9a17f268b2f; flrbcr=1481689657-2f0f82427fcc334894bfc315cd7684598f5ca022; flrbrst=1481689657-68440532ed47973c66b169ea8b6a9fe0848612dd; flrtags=1481689657-11b7b143b8865bc470e8fd0de34f6567a60b60cf; flrbfd=1481689657-d19ffbc18766dc64005d7c0428bf0499de2fa3cd; flrb=15; _ga=GA1.2.1444836269.1481684215; vp=653%2C631%2C1.5%2C10%2Csearch-photos-everyone-view%3A653%2Csearch-photos-contacts-view%3A653%2Cphotolist-container%3A961%2Cfavorites-page-view%3A961%2Calbums-list-page-view%3A961',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'
    }

    page_num = 1
    count = 0
    people_info = dict()
    error_count = 0

    url = 'https://api.flickr.com/services/rest?sort=' \
          'date-posted-desc&parse_tags=1&content_type=' \
          '7&extras=can_comment%2Ccount_comments%2Ccount_faves%2C' \
          'description%2Cisfavorite%2Clicense%2Cmedia%2Cneeds_interstitial%2' \
          'Cowner_name%2Cpath_alias%2Crealname%2Crotation%2Curl_c%2' \
          'Curl_l%2Curl_m%2Curl_n%2Curl_q%2Curl_s%2Curl_sq%2Curl_t%2' \
          'Curl_z&per_page=50&' \
          'page=' + str(page_num) + \
          '&lang=en-US&text=&advanced=1&' \
          'min_upload_date=' + start_time + \
          '&' \
          'max_upload_date=' +end_time+ \
          '&' \
          'viewerNSID=145786923%40N07&' \
          'method=flickr.photos.search&' \
          'csrf=1481717321%3Ad7y667lpnak0529%3' \
          'Aaaaa004c0dd00396c6b5bf3b4bfcf45c&' \
          'api_key=d10e2e0e542b25f9506778cf4768341d&' \
          'format=json&hermes=1&hermesClient=1&' \
          'reqId=ab0920b2&nojsoncallback=1'

    r = requests.get(url, headers=headers)

    data_js = json.loads(r.text.encode('utf-8'))
    total_num = data_js['photos']['total']

    for people_js in data_js['photos']['photo']:
        count += 1

        try:
            people_info['post_pic_url'] = people_js['url_z_cdn']
        except KeyError:
            print 'no post url'

        try:
            people_info['owner_id'] = people_js['owner']
        except KeyError:
            print 'no owner id'

        try:
            people_info['realname'] = people_js['realname']
        except KeyError:
            print 'no real name'

        try:
            people_info['ownername'] = people_js['ownername']
        except KeyError:
            print 'no owner name'

        r = requests.get('https://www.flickr.com/people/%s/' % people_info['owner_id'])

        soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')
        try:
            profile_details = soup.find('div', {'id': 'a-bit-more-about'})
            profile_details_parts = profile_details.findAll('dl')

            for profile_details_part in profile_details_parts:
                profile_details_name = profile_details_part.find('dt').string.\
                    replace(' ', '').replace(':', '').lower()

                if 'name' == profile_details_name:
                    pass

                else:
                    profile_details_name_value_seg = profile_details_part.find('dd')

                    while profile_details_name_value_seg.find('span') is not None:
                        profile_details_name_value_seg = profile_details_name_value_seg.find('span')

                    profile_details_value = profile_details_name_value_seg.string.\
                        replace('\n', '').replace(':', '').replace('\r', '').replace('\t', '')

                    people_info[profile_details_name] = profile_details_value

            error_count = 0

            bio_div = soup.find('p', {'class' : 'note'})
            if bio_div is not None:
                people_info['bio'] = bio_div.string
            else:
                print 'user does not have bio'

            profile_img_div = soup.find('img', {'class': 'sn-avatar-ico'})
            if profile_img_div is not None:
                people_info['profile_pic_url'] = profile_img_div['src']
            else:
                print 'user does not have profile picture'

        except Exception as e:
            print 'First Inner Exception: ' + str(e)
            if error_count >= 50:
                print 'unknow error, terminating program'
                return
            error_count += 1
            time.sleep(3)
            pass

        print 'writing user %s.' % people_info['ownername']
        outputfile = open(outputfilepath, 'a')
        json.dump(people_info.copy(), outputfile)
        outputfile.write('\n')
        people_info.clear()
        outputfile.close()

    print 'current data number %d' % count

    while count < total_num:

        page_num += 1

        url = 'https://api.flickr.com/services/rest?sort=' \
              'date-posted-desc&parse_tags=1&content_type=' \
              '7&extras=can_comment%2Ccount_comments%2Ccount_faves%2C' \
              'description%2Cisfavorite%2Clicense%2Cmedia%2Cneeds_interstitial%2' \
              'Cowner_name%2Cpath_alias%2Crealname%2Crotation%2Curl_c%2' \
              'Curl_l%2Curl_m%2Curl_n%2Curl_q%2Curl_s%2Curl_sq%2Curl_t%2' \
              'Curl_z&per_page=50&' \
              'page=' + str(page_num) + \
              '&lang=en-US&text=&advanced=1&' \
              'min_upload_date=' + start_time + \
              '&' \
              'max_upload_date=' + end_time + \
              '&' \
              'viewerNSID=145786923%40N07&' \
              'method=flickr.photos.search&' \
              'csrf=1481717321%3Ad7y667lpnak0529%3' \
              'Aaaaa004c0dd00396c6b5bf3b4bfcf45c&' \
              'api_key=d10e2e0e542b25f9506778cf4768341d&' \
              'format=json&hermes=1&hermesClient=1&' \
              'reqId=ab0920b2&nojsoncallback=1'

        r = requests.get(url, headers=headers)

        data_js = json.loads(r.text.encode('utf-8'))

        for people_js in data_js['photos']['photo']:
            count += 1

            try:
                people_info['post_pic_url'] = people_js['url_z_cdn']
            except KeyError:
                print 'no post url'

            try:
                people_info['owner_id'] = people_js['owner']
            except KeyError:
                print 'no owner id'

            try:
                people_info['realname'] = people_js['realname']
            except KeyError:
                print 'no real name'

            try:
                people_info['ownername'] = people_js['ownername']
            except KeyError:
                print 'no owner name'

            r = requests.get('https://www.flickr.com/people/%s/' % people_info['owner_id'])

            soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')
            try:
                profile_details = soup.find('div', {'id': 'a-bit-more-about'})
                profile_details_parts = profile_details.findAll('dl')

                for profile_details_part in profile_details_parts:
                    profile_details_name = profile_details_part.find('dt').string. \
                        replace(' ', '').replace(':', '').lower()

                    if 'name' == profile_details_name:
                        pass

                    else:
                        profile_details_name_value_seg = profile_details_part.find('dd')

                        while profile_details_name_value_seg.find('span') is not None:
                            profile_details_name_value_seg = profile_details_name_value_seg.find('span')

                        profile_details_value = profile_details_name_value_seg.string. \
                            replace('\n', '').replace(':', '').replace('\r', '').replace('\t', '')

                        people_info[profile_details_name] = profile_details_value

                error_count = 0
            except Exception as e:
                print 'First Inner Exception: ' + str(e)
                if error_count >= 50:
                    print 'unknow error, terminating program'
                    return
                error_count += 1
                time.sleep(3)

            print 'writing user %s.' % people_info['ownername']
            outputfile = open(outputfilepath, 'a')
            json.dump(people_info.copy(), outputfile)
            outputfile.write('\n')
            people_info.clear()
            outputfile.close()

        print 'current data number %d' % count



if __name__ == '__main__':
    # crawl_info_based_on_time('1480741199', '1480741199', 'test.txt')
    pass
# -*- coding: utf-8 -*-
import json
import pandas
from misc import load_categories, add_category_to_business, two_to_one_mode, one_mode_filter


source_dir = '/media/data/course resource/社群網路分析/yelp_dataset_challenge_round9/'
dest_dir = '/media/data/course resource/社群網路分析/parsed_data/model1/'


def load_user(user_ids):
    source_path = source_dir + 'yelp_academic_dataset_user.json'
    user_path = dest_dir + 'user.csv'
    friendship_path = dest_dir + 'friendship.tsv'
    basic_fields = ['Id', 'review_count', 'average_stars', 'useful', 'fans', 'type']  # all numeric except user_id
    special_fields = ['yelping_since']  # date_string

    cur = 0
    valid_cur = 0
    all_user_data = []  # list of list, without column name
    # build list of rows
    with open(source_path, 'r') as source_file, open(friendship_path, 'w') as friendship_file:
        # use some basic filter? like review_count >= 10
        for line in source_file:
            if cur % 10000 == 0:
                print("working on user #{0}, current valid user: {1}".format(cur, valid_cur))
            cur += 1
            row = json.loads(line.strip())
            # print(row)
            if row['user_id'] not in user_ids:
                continue
            valid_cur += 1
            user_attr = [
                unicode(row['user_id']),
                int(row['review_count']),  # 原本因 data type 為 unicode, 被視為字串排序
                float(row['average_stars']),
                int(row['useful']),
                int(row['fans']),
                u'user'
            ]
            all_user_data.append(user_attr)
            for friend_id in row['friends']:  # 備用, 姑且先不論沒發評價, 但是屬於某個發評價的人的朋友
                friendship_file.write("{0}\t{1}\t{2}\n".format(row['user_id'], friend_id, 'Undirected'))

            if len(all_user_data) >= len(user_ids):  # already get all user data
                break

    # transform to dataframe
    df = pandas.DataFrame(all_user_data, columns=basic_fields)
    df.to_csv(user_path, index=False, encoding='utf-8')  # dump dataframe to csv file

    return df['Id'].tolist()  # user_id


def business_by_city(file_path):
    """
    878 cities
    (u'Las Vegas', 22891), (u'Toronto', 14539), (u'Phoenix', 14467) has most business
    :param file_path:
    :return:
    """
    cities = {}
    with open(file_path, 'r') as source_file:
        for line in source_file:
            row = json.loads(line.strip())
            if row['city'] not in cities:
                cities[row['city']] = 0
            else:
                cities[row['city']] += 1
    print(len(cities))
    sorted_cities = sorted(cities.items(), key=lambda x: x[1], reverse=True)
    print(sorted_cities)


def load_business(city):
    source_path = source_dir + 'yelp_academic_dataset_business.json'
    dest_path = dest_dir + 'business.csv'
    categories_path = dest_dir + 'business_categories.tsv'
    basic_fields = ['Id', 'name', 'city', 'latitude', 'longitude', 'stars', 'review_count', 'type']  # 部份數值作為weight?

    cur = 0
    all_business_data = []  # list of list, without column name
    with open(source_path, 'r') as source_file, open(categories_path, 'w') as categories_file:
        for line in source_file:
            if cur % 10000 == 0:
                print("working on business #{0}".format(cur))
            cur += 1
            row = json.loads(line.strip())
            if row['city'] != city:
                continue
            business_attr = [
                unicode(row['business_id']),
                unicode(row['name']),
                unicode(row['city']),
                float(row['latitude']),
                float(row['longitude']),
                int(row['stars']),
                int(row['review_count']),
                u'business'
            ]
            # print(business_attr)
            all_business_data.append(business_attr)
            if row['categories']:  # some might be None
                categories_file.write(row['business_id'] + "\t" + ",".join(row['categories']) + "\n")
    # transform to dataframe
    df = pandas.DataFrame(all_business_data, columns=basic_fields)
    # sort by review_count, get only the most 3000
    df = df.sort_values("review_count", ascending=False)[:3000]

    df.to_csv(dest_path, index=False, encoding='utf-8')  # dump dataframe to csv file
    return df['Id'].tolist()  # business_id


def load_reviews(business_ids):
    source_path = source_dir + 'yelp_academic_dataset_review.json'
    dest_path = dest_dir + 'review.csv'
    basic_fields = ['review_id', 'user_id', 'business_id', 'stars']  # 作為weight?

    review_ids = []
    # user_ids = set()
    cur = 0
    all_review_data = []  # list of list, without column name
    with open(source_path, 'r') as source_file:
        for line in source_file:
            if cur % 10000 == 0:
                print("working on review #{0}".format(cur))
            cur += 1
            row = json.loads(line.strip())
            if row['business_id'] not in business_ids:
                continue
            review_attr = [
                row['user_id'], row['business_id'], row['stars']
            ]
            all_review_data.append(review_attr)
            review_ids.append(row['review_id'])
            # user_ids.add(row['user_id'])
    df = pandas.DataFrame(all_review_data, columns=["source", "target", "weight"])
    df.to_csv(dest_path, index=False, encoding='utf-8')  # dump dataframe to csv file
    return review_ids, df['source'].unique().tolist()  # review ids and user ids


if __name__ == '__main__':
    # business_by_city(source_dir + 'yelp_academic_dataset_business.json')
    """
    b_ids = load_business(u'Las Vegas')  # filter 'Las Vegas', store business_ids
    print("Las Vegas business count: {}".format(len(b_ids)))
    r_ids, u_ids = load_reviews(b_ids)  # filter business in Las Vegas, store user_ids
    print("Las Vegas review count: {}".format(len(r_ids)))
    print("Las Vegas review-user count: {}".format(len(u_ids)))
    load_user(u_ids)  # filter user_ids
    add_category_to_business(dest_dir)
    """

    """
    方案: 直接降維到1 mode on business 的 model
    1. 對目前資料中所有的user, 找到所有的 review link
    2. 把 review link 的 business_id 取出
    3. 針對該 user, 排列組合所有的 business_id 為 1 mode edge
    4. 累加次數作為 edge weight (可能有多個 user 疊加同一 edge)
    """
    # two_to_one_mode(dest_dir)
    one_mode_filter(dest_dir, 5)

# -*- coding: utf-8 -*-
"""
2nd model: 基於去過多個 city 的 user 篩選
觀察 city 間關係, 或是跨 city 的 business 關係
"""

import json
import pandas
from misc import load_categories, add_category_to_business, two_to_one_mode, one_mode_filter

source_dir = '/media/data/course resource/社群網路分析/yelp_dataset_challenge_round9/'
dest_dir = '/media/data/course resource/社群網路分析/parsed_data/model2/'


def load_user(quantity):
    source_path = source_dir + 'yelp_academic_dataset_user.json'
    user_path = dest_dir + 'user.csv'
    friendship_path = dest_dir + 'friendship.csv'
    basic_fields = ['Id', 'review_count', 'average_stars', 'useful', 'fans', 'type']  # all numeric except user_id
    special_fields = ['yelping_since']  # date_string

    cur = 0
    valid_cur = 0
    all_user_data = []  # list of list, without column name
    # build list of rows
    with open(source_path, 'r') as source_file:
        # use some basic filter? like review_count >= 10
        for line in source_file:
            if cur % 10000 == 0:
                print("working on user #{0}, current valid user: {1}".format(cur, valid_cur))
            cur += 1
            row = json.loads(line.strip())
            # print(row)
            if row['review_count'] < 30:
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

    # transform to dataframe
    df = pandas.DataFrame(all_user_data, columns=basic_fields)
    # sort data
    sorted_df = df.sort_values(by='review_count', ascending=False)  # may also use nested sort
    final_df = sorted_df[:quantity]
    # print(final_df[0:3])
    final_df.to_csv(user_path, index=False, encoding='utf-8')  # dump dataframe to csv file

    return final_df['Id'].tolist()  # user_id


def load_review(user_ids):
    source_path = source_dir + 'yelp_academic_dataset_review.json'
    dest_path = dest_dir + 'review.csv'
    basic_fields = ['review_id', 'user_id', 'business_id', 'stars']  # 作為weight?

    review_ids = []
    business_ids = set()
    cur = 0
    all_review_data = []  # list of list, without column name
    with open(source_path, 'r') as source_file:
        for line in source_file:
            if cur % 10000 == 0:
                print("working on review #{0}".format(cur))
            cur += 1
            row = json.loads(line.strip())
            if row['user_id'] not in user_ids:
                continue
            review_attr = [
                row['user_id'], row['business_id'], row['stars']
            ]
            all_review_data.append(review_attr)
            review_ids.append(row['review_id'])
            business_ids.add(row['business_id'])
    df = pandas.DataFrame(all_review_data, columns=["source", "target", "weight"])
    df.to_csv(dest_path, index=False, encoding='utf-8')  # dump dataframe to csv file
    return review_ids, list(business_ids)


def load_business(business_ids):
    source_path = source_dir + 'yelp_academic_dataset_business.json'
    dest_path = dest_dir + 'business.csv'
    categories_path = dest_dir + 'business_categories.tsv'
    basic_fields = ['Id', 'name', 'city', 'latitude', 'longitude', 'stars', 'review_count', 'type']  # 部份數值作為weight?

    cur = 0
    valid_business_ids = []
    all_business_data = []  # list of list, without column name
    with open(source_path, 'r') as source_file, open(categories_path, 'w') as categories_file:
        for line in source_file:
            if cur % 10000 == 0:
                print("working on business #{0}".format(cur))
            cur += 1
            row = json.loads(line.strip())
            if row['business_id'] not in business_ids:
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
            valid_business_ids.append(row['business_id'])

            if len(all_business_data) >= len(business_ids):  # already get all user data
                break

    # transform to dataframe
    df = pandas.DataFrame(all_business_data, columns=basic_fields)
    df.to_csv(dest_path, index=False, encoding='utf-8')  # dump dataframe to csv file
    return valid_business_ids


if __name__ == '__main__':
    """
    top_n = 5000
    u_ids = load_user(top_n)  # get top 10000 active users
    """

    """ load u_ids form parsed user data
    """
    u_data = pandas.DataFrame.from_csv(dest_dir + 'user.csv', index_col=None)
    print(u_data[:3])
    u_ids = u_data['Id'].tolist()

    """
    r_ids, b_ids = load_review(u_ids)  # get reviews by user_ids, and return business_ids
    print("review count of top {0} active users: {1}".format(top_n, len(r_ids)))
    print("business reviewed by top {0} active users: {1}".format(top_n, len(b_ids)))
    """

    """ load b_ids form parsed review data
    r_data = pandas.DataFrame.from_csv(dest_dir + 'review.csv', index_col=None)
    print(len(r_data))
    b_ids = r_data['target'].unique()
    print(len(b_ids))
    """

    """
    valid_b_ids = load_business(b_ids)  # get business by business_ids
    print("valid business count relate to top {0} active users: {1}".format(top_n, len(valid_b_ids)))
    """

    # add_category_to_business(dest_dir)
    two_to_one_mode(dest_dir, user_ids=u_ids)  # failed, due to local topology from star to mesh, too many links
    one_mode_filter(dest_dir, 5)

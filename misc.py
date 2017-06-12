# -*- coding: utf-8 -*-
import pandas


def load_categories(source_path):
    """
    得到所有資料中有的分類
    除了建立 business 對 categories 的 map 之外,
    將 category 依出現次數排序,
    對每個 business 來說, 他的主要 category 便是 在累計次數中出現最多次的 category
    以此方法篩選出來的 category, 理論會是產業別 (考慮去掉 Restaurants 這個出現次數明顯較多的類型)
    :param source_path:
    :return:
    """
    # source_path = dest_dir + "business_categories.tsv"
    business_categories = {}
    categories_accumulator = {}
    with open(source_path, 'r') as source_file:
        for line in source_file:
            tmp = line.strip().split('\t')
            categories = tmp[1].split(',')
            for category in categories:
                if category not in categories_accumulator:
                    categories_accumulator[category] = 1
                else:
                    categories_accumulator[category] += 1
            business_categories[tmp[0]] = categories
    tmp = [list(item) for item in categories_accumulator.items()]
    df = pandas.DataFrame(tmp, columns=["name", "count"])
    df = df.sort_values("count", ascending=False)
    print(df[:100])

    return categories_accumulator, business_categories


def add_category_to_business(dest_dir):
    stop_category = ["Restaurants", "Food"]  # too many using this category

    categories_count, business_categories = load_categories(dest_dir + "business_categories.tsv")
    b_data = pandas.DataFrame.from_csv(dest_dir + "business.csv", index_col=None)

    business_category = []
    for business in business_categories:
        selected_category = ""
        selected_category_count = 0
        for category in business_categories[business]:
            if category in categories_count and category not in stop_category \
                    and categories_count[category] > selected_category_count:
                selected_category = category
                selected_category_count = categories_count[category]
        business_category.append(selected_category)

    b_data['category'] = pandas.Series(business_category)
    b_data.to_csv(dest_dir + "business2.csv", index=False, encoding='utf-8')


def two_to_one_mode(dest_dir, user_ids=None):
    source_path = dest_dir + 'review.csv'
    dest_path = dest_dir + 'business_shared_user.csv'
    df = pandas.DataFrame.from_csv(source_path, index_col=None, encoding="utf-8")

    # build business_ids from the same user
    user_to_business = {}  # key is user_id, value is [business_ids]
    cur = 0
    for row in df.to_records():
        if cur % 1e4 == 0:
            print("working on review #{0}".format(cur))
        cur += 1
        user_id, business_id, stars = row[1], row[2], row[3]
        if user_ids is not None and user_id not in user_ids:
            continue
        if user_id in user_to_business:
            user_to_business[user_id].append(business_id)
        else:
            user_to_business[user_id] = [business_id]
    print("valid user: {0}".format(len(user_to_business)))

    # accumulate shared users between two business
    between_business = {}
    cur = 0
    for user_id in user_to_business:
        if cur % 1e2 == 0:
            print("working on user #{0}".format(cur))
            print("between_business len: {0}".format(len(between_business)))
        business_ids = user_to_business[user_id]
        # build business pair, and check/accumulate the weight of pair(edge)
        last = len(business_ids)
        bid_cur = 0
        for val in business_ids:
            if bid_cur == last:
                break
            for val_2 in business_ids[bid_cur+1:]:
                pair = {val, val_2}
                key = "_".join(pair)
                if key in between_business:
                    between_business[key] += 1
                else:
                    between_business[key] = 1
            bid_cur += 1
        cur += 1


    # transform to list of (business1, business2, relate), len(business_id) == 22
    list_to_df = []
    cur = 0
    for business_pair in between_business:
        shared = between_business[business_pair]
        if cur % 1e4 == 0:
            print("working on business pair #{0}".format(cur))
        row = [business_pair[:22], business_pair[23:], shared]
        list_to_df.append(row)
        cur += 1

    one_mode_df = pandas.DataFrame(list_to_df, columns=["source", "target", "weight"])
    one_mode_df.to_csv(dest_path, index=False, encoding='utf-8')  # dump dataframe to csv file
    print("two_to_one_mode done.")


def one_mode_filter(dest_dir, n):
    source_path = dest_dir + 'business_shared_user.csv'
    dest_path = dest_dir + 'business_shared_user2.csv'
    df = pandas.DataFrame.from_csv(source_path, index_col=None, encoding="utf-8")
    print(df.shape)
    q_df = df.query("weight > {0}".format(n))
    print(q_df.shape)
    q_df.to_csv(dest_path, index=False, encoding='utf-8')  # dump dataframe to csv file

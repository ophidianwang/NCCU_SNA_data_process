# -*- coding: utf-8 -*-
"""
3rd model: 基於 model2, 將 category 作為 node, 基於 shared business 建立 edge
觀察 category 間關係, 或是跨 city 的 business 關係
"""

import json
import pandas
from misc import load_categories, add_category_to_business, two_to_one_mode, one_mode_filter

source_dir = '/media/data/course resource/社群網路分析/parsed_data/model2/'
dest_dir = '/media/data/course resource/社群網路分析/parsed_data/model3/'

source_path = source_dir + 'business.csv'
categories_path = source_dir + 'business_categories.tsv'

category_nodes = dest_dir + 'category_nodes.csv'
category_edges = dest_dir + 'category_edges.csv'


def get_category_no(category, category_list):
    try:
        category_no = category_list.index(category)  # find # if already exist
    except ValueError as err:
        category_list.append(category)
        category_no = len(category_list) - 1  # new category's #
    return category_no


def category_graph():
    business_cur = 0
    category_list = []
    between_category = {}  # edges[from_to] = weight
    with open(categories_path, 'r') as source_file:
        for line in source_file:
            if business_cur % 1e3 == 0:
                print("working on business #{0}".format(business_cur))
            business_cur += 1
            tmp = line.strip().split('\t')
            categories = tmp[1].split(',')
            last = len(categories)
            category_cur = 0
            for category_1 in categories:
                if category_cur == last:
                    break
                # add new category node or not
                category_no_1 = get_category_no(category_1, category_list)  # find # if already exist
                for category_2 in categories[category_cur + 1:]:
                    category_no_2 = get_category_no(category_2, category_list)
                    pair = {category_no_1, category_no_2}
                    key = "{0}_{1}".format(*pair)
                    if key in between_category:
                        between_category[key] += 1
                    else:
                        between_category[key] = 1
                category_cur += 1
    print("# of categories: {0}".format(len(category_list)))
    # print(category_list)
    print("# of edges: {0}".format(len(between_category)))
    # print(between_category)

    node_df = pandas.DataFrame(category_list, columns=["category"])
    node_df['id'] = pandas.Series(range(len(category_list)))
    node_df['type'] = pandas.Series(['category']*len(category_list))
    print(node_df)

    list_to_df = []
    cur = 0
    for category_pair in between_category:
        shared = between_category[category_pair]
        if cur % 1e4 == 0:
            print("working on business pair #{0}".format(cur))
        tmp = category_pair.split('_')
        row = [tmp[0], tmp[1], shared]
        list_to_df.append(row)
        cur += 1
    edge_df = pandas.DataFrame(list_to_df, columns=["source", "target", "weight"])
    # print(edge_df)

    node_df.to_csv(category_nodes, index=False, encoding='utf-8')  # dump dataframe to csv file
    edge_df.to_csv(category_edges, index=False, encoding='utf-8')  # dump dataframe to csv file


def main():
    category_graph()


if __name__ == '__main__':
    main()

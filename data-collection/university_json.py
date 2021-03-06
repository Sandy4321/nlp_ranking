import pandas as pd
from os import walk
from collections import Counter
import timeit
from collections import defaultdict


def university_pub():

    universities = pd.read_csv('us_universities.tsv', sep='\t', names=['university', 'domain', 'city', 'state'])


    uni = {}

    for u in universities['domain']:
        uni[u] = []

    for (dirpath, dirnames, filenames) in walk('./pub_json/'):
        for filename in filenames:
            pub = pd.read_json(dirpath + filename)
            records = pub.to_dict(orient='records')
            # print(records)

            for record in records:
                domains = [parse_email(e.split('@')[-1]) for e in record['emails']]
                # print(record['emails'])
                c = Counter(domains)
                for key in c.keys():
                    if key in uni.keys():
                        # (pub_id, year, contribution_percentage)
                        uni[key].append((record['id'], record['year'], c[key]/len(record['authors'])))



    print(uni)

    university_list = []
    for k,v in uni.items():
        name = universities[universities['domain'] == k]['university'].values[0]
        university_list.append({'domain_id': k, 'name': name, 'publications': v})

    df = pd.DataFrame(university_list)
    df.to_json('university.json', orient='records')


def university_pub2():

    universities = pd.read_csv('us_universities.tsv', sep='\t', names=['university', 'domain', 'city', 'state'])


    uni = {}


    for (dirpath, dirnames, filenames) in walk('./pub_json/'):
        for filename in filenames:
            if '.json' in filename:
                pub = pd.read_json(dirpath + filename)
                records = pub.to_dict(orient='records')
                # print(records)

                for record in records:
                    domains = [parse_email(e.split('@')[-1]) for e in record['emails']]
                    # print(record['emails'])
                    c = Counter(domains)
                    for key in c.keys():
                        if key in universities['domain'].tolist():
                            if key in uni.keys():
                                # (pub_id, year, contribution_percentage)
                                uni[key].append((record['id'], c[key]/len(record['authors'])))
                            else:
                                uni[key] = [(record['id'], c[key]/len(record['authors']))]



    print(uni)

    university_list = []
    for k,v in uni.items():
        name = universities[universities['domain'] == k]['university'].values[0]
        university_list.append({'domain_id': k, 'publications': v})

    df = pd.DataFrame(university_list)
    df.to_json('university.json', orient='records')








def parse_email(domain):
    if '.edu' in domain:
        d = domain.split('.')
        return '.'.join(d[d.index('edu')-1:])
    else:
        return domain

# - classify by school by year
# - for each publication: alpha/# of authors * type of the venue
import json
def author_score():


    university = pd.read_json('university.json', orient='records')
    bibmap = json.load(open('bibmap.json'))

    venue_pub = {} # only look at publications with authors from an university institution
    for pub_id in [y[0] for x in university['publications'].values.tolist() if x for y in x]:
        venue = find_venue(pub_id)
        if venue in venue_pub.keys():
            venue_pub[venue].append(pub_id)
        else:
            venue_pub[venue] = [pub_id]

    # scoring each venue type
    score = {'journal': 3, 'top-conference': 3, 'conference': 3, 'workshop': 1, 'demonstration': 1}


    # authors = {author_id: {2019: {university1_domain: score, university2_domain: score}}}
    authors = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))


    empty = []

    for k,v in venue_pub.items():
        bib = next((y for y in bibmap if y['id'] == k), None)
        with open('./pub_json/'+ k+'.json') as p:
            json_file = json.load(p)
            venue_score = score[bib['type']]
            for pub in [x for x in json_file if x['id'] in v]:
                for i in range(len(pub['authors'])):
                    if '.edu' in pub['emails'][i]:
                        author_id = pub['author_id'][i]
                        if author_id == '':
                            empty.append(k)
                        year = pub['year']
                        uni_domain = parse_email(pub['emails'][i].split('@')[1])
                        authors[author_id][year][uni_domain] += 1 / len(pub['authors']) * venue_score



    print(authors['jinho-d-choi'])



def find_venue(pub_id):
    if 'W' in pub_id:
        return pub_id[:-2]
    else:
        return pub_id[:-3]

def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped






if __name__ == '__main__':
    # university_pub()
    ['cs.utexas.edu', 'cs.utexas.edu', 'cs.utexas.edu']
    # print(parse_email('mail.neu.edu.cn'))

    # wrapped = wrapper(find_venue, 'C10-2001')
    # print(timeit.timeit(wrapped, number=6866))
    print(timeit.timeit(author_score, number=1))


    # author_score()

    # authors = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))
    # authors['a']['b']['c'] += 1/3
    # print(authors['a']['b']['c'])
    # university_pub2()
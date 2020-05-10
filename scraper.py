import re
import requests
from time import sleep
from bs4 import BeautifulSoup
from utils import get_value, get_bool, get_value_str_txt, is_empty


class NovelScraper(object):
    """
    Scrapes novel information from novelupdates, http://www.novelupdates.com/.
    
    Constant web links:
    * NOVEL_LIST_URL: http://www.novelupdates.com/novelslisting/?st=1&pg=
      The url of the series listings. A number is added to the end dependingo n the tab wanted.
    * NOVEL_SINGLE_URL: http://www.novelupdates.com/?p=
      The url of a single novel, a id number needs to be added to the end for the specific novel.
    
    :param debug: Boolean, debug mode. If true, only one page with novels will be parsed (25).
    :param delay: The delay between web requests, used both when obtaining novel ids and for each individual novel.
                  Affects the speed of the program.
    """

    def __init__(self, debug=False, delay=0.5):
        self.debug = debug
        self.delay = delay
        self.NOVEL_LIST_URL = "http://www.novelupdates.com/novelslisting/?st=1&pg="
        self.NOVEL_SINGLE_URL = "http://www.novelupdates.com/?p="

    def parse_all_novels(self):
        """
        Parses and scrapes information from all novel pages.
        :returns: A list of dictionaries with all scraped and cleaned information of the novels.
        """
        novel_ids = self.get_all_novel_ids(delay=delay)

        all_novel_information = []
        for novel_id in novel_ids:
            novel_info = self.parse_single_novel(novel_id)
            all_novel_information.append(novel_info)
            sleep(self.delay)
        return all_novel_information

    def parse_single_novel(self, novel_id):
        """
        Parses and scrapes information from a single novel page.

        :param novel_id: The id number of the novel.
        :returns: A dictinary with all scraped and cleaned information about the novel.
        """

        page = requests.get(self.NOVEL_SINGLE_URL + str(novel_id))
        soup = BeautifulSoup(page.content, 'html5lib')
        content = soup.find('div', attrs={'class': 'w-blog-content'})
        if content is None:
            return dict()

        print("Processing novel: " + str(novel_id))

        data = {'id': novel_id}
        data.update(self.general_info(content))
        data.update(self.publisher_info(content))
        data.update(self.chapter_info(content))
        data.update(self.release_info(content))
        data.update(self.community_info(content))
        data.update(self.relation_info(content))

        return data

    def get_all_novel_ids(self):
        """
        There is no easy way to get all novel ids (they are not strictly consecutive).
        Gets all novel ids from the novels listing page. The page contains multiple tabs with novels, first
        the maximum number of pages is obtained and then these are iterated through.

        :param delay: Delay between web requests.
        :returns: A list with the novel ids of all currently listed novels.
        """

        if self.debug:
            novels_num_pages = 1
            print("Debug run, running with: " + str(novels_num_pages))
        else:
            page = requests.get(self.NOVEL_LIST_URL + '1')
            novels_num_pages = self.get_novel_list_num_pages(page)
            print("Full run, pages with novels: " + str(novels_num_pages))

        all_novel_ids = []
        for i in range(1, novels_num_pages + 1):
            page = requests.get(self.NOVEL_LIST_URL + str(i))
            novel_ids = self.get_novel_ids(page)
            all_novel_ids.extend(novel_ids)
            sleep(self.delay)
        return all_novel_ids

    def get_novel_list_num_pages(self, page):
        """
        Get the maximum number of pages with novels.
        This number is not contant since the number of novels on the website are increasing.
        Following the current website layout each page have 25 novels.

        :param page: The web address to the novel list, presumably the first page but can be any.
        :returns: An int representing the current number of pages of the novel lists.
        """
        soup = BeautifulSoup(page.text, 'html.parser')
        dig_pag = soup.find('div', attrs={'class': 'digg_pagination'})
        max_page = max([int(a.text) for a in dig_pag.find_all('a') if a.text.isdigit()])
        return max_page

    def get_novel_ids(self, page):
        """
        Gets all the novel ids from a page.

        :param page: One of the pages with novels.
        :returns: A list with all novel ids for the novels on the page.
        """
        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.find('div', attrs={'class': 'w-blog-content other'})
        novels = table.find_all('div', attrs={'class': 'search_title'})
        novel_ids = [novel.find('span', attrs={'class': 'rl_icons_en'}).get('id')[3:] for novel in novels]
        novel_ids = [int(n) for n in novel_ids]
        return novel_ids

    def general_info(self, content):
        """
        Scrapes all general information of a specific novel.

        :param content: The content page of a novel.
        :returns: A dictionary with scraped and cleaned information.
        """

        gen_info = dict()
        gen_info['name'] = get_value(content.find('div', attrs={'class', 'seriestitlenu'}))
        gen_info['assoc_names'] = get_value(content.find('div', attrs={'id': 'editassociated'}),
                                            check=lambda e: e, parse=lambda e: list(e.stripped_strings))
        gen_info['original_langauge'] = get_value(content.find('div', attrs={'id': 'showlang'}),
                                                  lambda e: e.a,
                                                  lambda e: e.text.strip().lower())
        gen_info['authors'] = [author.text.lower()
                               for author in content
                                   .find('div', attrs={'id': 'showauthors'})
                                   .find_all('a')]
        gen_info['genres'] = [genre.text.lower()
                              for genre in content
                                  .find('div', attrs={'id': 'seriesgenre'})
                                  .find_all('a', attrs={'class': 'genre'})]
        gen_info['tags'] = [tag.text.lower()
                            for tag in content
                                .find('div', attrs={'id': 'showtags'})
                                .find_all('a')]
        return gen_info

    def publisher_info(self, content):
        """
        Scrapes all publisher information of a specific novel.

        :param content: The content page of a novel.
        :returns: A dictionary with scraped and cleaned information.
        """
        pub_info = dict()
        pub_info['start_year'] = get_value(content.find('div', attrs={'id': 'edityear'}), )
        pub_info['licensed'] = get_bool(get_value(content.find('div', attrs={'id': 'showlicensed'})))
        pub_info['original_publisher'] = get_value(content.find('div', attrs={'id': 'showopublisher'}),
                                                   lambda e: e.a,
                                                   lambda e: e.a.string.strip().lower())
        pub_info['english_publisher'] = get_value(content.find('div', attrs={'id': 'showepublisher'}),
                                                  lambda e: e.a,
                                                  lambda e: e.a.string.strip().lower())
        return pub_info

    def chapter_info(self, content):
        """
        Scrapes all chapter information of a specific novel.
        Both latest released chapters and if the novel is complete.

        :param content: The content page of a novel.
        :returns: A dictionary with scraped and cleaned information.
        """
        chap_info = dict()
        chapter_status = get_value_str_txt(content.find('div', attrs={'id': 'editstatus'}))

        if chapter_status is not None:
            chap_info['complete_original'] = 'complete' in chapter_status.lower()
            chapter_current = re.search('(\d+)[ wnl]*(?=chap)', chapter_status.lower())
            if chapter_current is not None:
                chapter_current = chapter_current.group(1).strip() + " chapters"
            else:
                # Check if volume
                chapter_current = re.search('(\d+)[ wnl]*(?=volu)', chapter_status.lower())
                if chapter_current is not None:
                    chapter_current = chapter_current.group(1).strip() + " volumes"
                else:
                    # Get the first number
                    chapter_current = re.search('(\d+)', chapter_status.lower())
                    if chapter_current is not None:
                        chapter_current = chapter_current.group(1).strip()

            chap_info['chapters_original_current'] = chapter_current if chapter_current != "" else None
        chap_info['complete_translated'] = get_bool(get_value(content.find('div', attrs={'id': 'showtranslated'})))

        table = content.find('table', attrs={'id': 'myTable'})
        if table is not None:
            release_table = table.find('tbody')
            chap_info['chapter_latest_translated'] = release_table.find('tr').find_all('td')[2].a.string.strip()
        return chap_info

    def release_info(self, content):
        """
        Scrapes all release and activity information of a specific novel.

        :param content: The content page of a novel.
        :returns: A dictionary with scraped and cleaned information.
        """
        rel_info = dict()
        release_freq = content.find('h5', attrs={'class': 'seriesother'}, string='Release Frequency').next_sibling
        activity = content.find_all('span', attrs={'class': 'userrate rank'})

        if not is_empty(release_freq):
            rel_info['release_freq'] = float(re.search('\d+\.?\d*', release_freq).group(0))

        rel_info['activity_week_rank'] = int(activity[0].string[1:])
        rel_info['activity_month_rank'] = int(activity[1].string[1:])
        rel_info['activity_all_time_rank'] = int(activity[2].string[1:])
        return rel_info

    def community_info(self, content):
        """
        Scrapes all community information of a specific novels.

        :param content: The content page of a novel.
        :returns: A dictionary with scraped and cleaned information.
        """
        comm_info = dict()
        activity = content.find_all('span', attrs={'class': 'userrate rank'})
        comm_info['on_reading_lists'] = int(content.find('b', attrs={'class': 'rlist'}).string)
        comm_info['reading_list_month_rank'] = int(activity[3].string[1:])
        comm_info['reading_list_all_time_rank'] = int(activity[4].string[1:])

        # rating
        rating_text = content.find('span', attrs={'class': 'uvotes'}).text.split(' ')
        comm_info['rating'] = float(rating_text[0][1:])
        comm_info['rating_votes'] = int(rating_text[3])
        return comm_info

    def relation_info(self, content):
        """
        Scrapes all relational information of a specific novel.

        :param content: The content page of a novel.
        :returns: A dictionary with scraped and cleaned information.
        """
        rel_info = dict()
        two_third_content = content.find('div', attrs={'class': 'two-thirds'})
        wpb_wrapper = two_third_content.find('div', attrs={'class': 'wpb_wrapper'})

        rel_info['related_series_ids'] = []
        rel_info['recommended_series_ids'] = []
        rel_info['recommendation_list_ids'] = []
        for series in wpb_wrapper.findChildren('a', attrs={'class': 'genre'}, recursive=False):
            if series.has_attr('title'):
                rel_info['recommended_series_ids'].append(series.get('id')[3:])
            else:
                rel_info['related_series_ids'].append(series.get('id')[3:])

        rec_lists = wpb_wrapper.find('ol', attrs={'class': 'ulc_sp'})
        if rec_lists:
            rel_info['recommendation_list_ids'] = [int(a['href'].split('/')[-2])
                                                   for a in rec_lists.findChildren('a')]

        # Return None in the cases where nothing is found (and not []).
        rel_info.update((k, None) for k, v in rel_info.items() if len(v) == 0)
        return rel_info

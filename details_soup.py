from bs4 import BeautifulSoup

import requests


class UsernameError(Exception):
    pass


class PlatformError(Exception):
    pass


class UserData:
    def __init__(self, username=None):
        self.__username = username

    def update_username(self, username):
        self.__username = username

    def __codechef(self):
        url = 'https://www.codechef.com/users/{}'.format(self.__username)

        page = requests.get(url)

        soup = BeautifulSoup(page.text, 'html.parser')

        try:
            rank = soup.find('div', class_='rating-number').text
        except AttributeError:
            raise UsernameError('User not Found')

        rating = soup.find('span', class_='rating').text

        rating_ranks_container = soup.find('div', class_='rating-ranks')
        rating_ranks = rating_ranks_container.find_all('a')

        global_rank = rating_ranks[0].strong.text
        country_rank = rating_ranks[1].strong.text

        def contests_details_get():
            rating_table = soup.find('table', class_='rating-table')

            rating_table_rows = rating_table.find_all('td')

            '''Can add ranking url to contests'''

            long_challenge = {'name': 'Long Challenge', 'rating': rating_table_rows[1].text,
                              'global rank': rating_table_rows[2].a.hx.text,
                              'country rank': rating_table_rows[3].a.hx.text}

            cook_off = {'name': 'Cook-off','rating': rating_table_rows[5].text,
                        'global rank': rating_table_rows[6].a.hx.text,
                        'country rank': rating_table_rows[7].a.hx.text}

            lunch_time = {'name': 'Lunch Time', 'rating': rating_table_rows[9].text,
                          'global rank': rating_table_rows[10].a.hx.text,
                          'country rank': rating_table_rows[11].a.hx.text}

            return [long_challenge, cook_off, lunch_time]

        details = {'rank': rank, 'rating': rating, 'global rank': global_rank, 'country rank': country_rank,
                   'contests': contests_details_get()}

        '''Can add latest contests details'''

        return details

    def __interviewbit(self):
        url = 'https://www.interviewbit.com/profile/{}'.format(self.__username)

        page = requests.get(url)

        if page.status_code != 200:
            raise UsernameError('User not Found')

        soup = BeautifulSoup(page.text, 'html.parser')
        details_main = soup.find('div', class_='user-stats')
        details_container = details_main.findChildren('div', recursive=False)

        details = {'status': 'Success', 'username': self.__username, 'platform': 'Interviewbit',
                   'rank': details_container[0].find('div', class_='txt').text,
                   'score': details_container[1].find('div', class_='txt').text,
                   'streak': details_container[2].find('div', class_='txt').text}

        return details

    def get_details(self, platform):
        if platform == 'interviewbit':
            return self.__interviewbit()

        if platform == 'codechef':
            return self.__codechef()

        raise PlatformError('Platform not Found')


if __name__ == '__main__':
    ud = UserData('abhijeet_ar')

    ans = ud.get_details('codechef')

    print(ans)

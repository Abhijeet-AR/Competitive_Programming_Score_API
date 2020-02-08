from bs4 import BeautifulSoup

import requests, json


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

            cook_off = {'name': 'Cook-off', 'rating': rating_table_rows[5].text,
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

    def __codeforces(self):
        url = 'https://codeforces.com/api/user.info?handles={}'.format(self.__username)

        page = requests.get(url)

        if page.status_code != 200:
            raise UsernameError('User not Found')

        details_api = page.json()

        if details_api['status'] != 'OK':
            raise UsernameError('User not Found')

        details_api = details_api['result'][0]

        details = {'status': 'Success', 'username': self.__username, 'platform': 'Codeforces',
                   'rating': details_api['rating'], 'max rating': details_api['maxRating'],
                   'rank': details_api['rank'], 'max rank': details_api['maxRank']}

        return details

    def __spoj(self):
        url = 'https://www.spoj.com/users/{}/'.format(self.__username)

        page = requests.get(url)

        soup = BeautifulSoup(page.text, 'html.parser')
        details_container = soup.find_all('p')

        points = details_container[2].text.split()[3][1:]
        rank = details_container[2].text.split()[2][1:]
        join_date = details_container[1].text.split()[1] + ' ' + details_container[1].text.split()[2]
        institute = ' '.join(details_container[3].text.split()[1:])

        def get_solved_problems():
            table = soup.find('table', class_='table table-condensed')

            rows = table.findChildren('td')

            solved_problems = []
            for row in rows:
                if row.a.text:
                    solved_problems.append(row.a.text)

            return solved_problems

        def get_todo():
            try:
                table = soup.find_all('table', class_='table')[1]
            except:
                return None

            rows = table.findChildren('td')

            todo_problems = []
            for row in rows:
                if row.a.text:
                    todo_problems.append(row.a.text)

            return todo_problems

        details = {'status': 'Success', 'username': self.__username, 'platform': 'SPOJ',
                   'points': points, 'rank': rank, 'solved': get_solved_problems(),
                   'todo': get_todo(), 'join data': join_date, 'institute': institute}

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
        if platform == 'codechef':
            return self.__codechef()

        if platform == 'codeforces':
            return self.__codeforces()

        if platform == 'spoj':
            try:
                return self.__spoj()
            except AttributeError:
                raise UsernameError('User not Found')

        if platform == 'interviewbit':
            return self.__interviewbit()

        raise PlatformError('Platform not Found')


if __name__ == '__main__':
    ud = UserData('abhijeet_ar')

    ans = ud.get_details('spoj')

    print(ans)

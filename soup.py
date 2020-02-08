from bs4 import BeautifulSoup

import requests


class UserData:
    def __init__(self, username):
        self.username = username

    def update_username(self, username):
        self.username = username

    def interviewbit(self):
        url = 'https://www.interviewbit.com/profile/{}'.format(self.username)

        page = requests.get(url)

        if page.status_code != 200:
            raise NameError('User not Found')

        soup = BeautifulSoup(page.text, 'html.parser')
        details_main = soup.find('div', class_='user-stats')
        details_container = details_main.findChildren('div', recursive=False)

        details = {'username': self.username, 'platform': 'Interviewbit',
                   'rank': details_container[0].find_all('div', class_='txt')[0].text,
                   'score': details_container[1].find_all('div', class_='txt')[0].text,
                   'streak': details_container[2].find_all('div', class_='txt')[0].text}

        return details

    def get_details(self, platform):
        if platform == 'interviewbit':
            return self.interviewbit()


if __name__ == '__main__':
    ud = UserData('abhijeet_ar')

    ans = ud.get_details('interviewbit')

    print(ans)
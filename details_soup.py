import json
import re
# DO NOT import this after requests
import grequests
import requests
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from util import get_safe_nested_key


class UsernameError(Exception):
    pass


class PlatformError(Exception):
    pass


class BrokenChangesError(Exception):
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
            rating = soup.find('div', class_='rating-number').text
        except AttributeError:
            raise UsernameError('User not Found')

        stars = soup.find('span', class_='rating')
        if stars:
            stars = stars.text

        highest_rating_container = soup.find('div', class_='rating-header')
        highest_rating = highest_rating_container.find_next('small').text.split()[-1].rstrip(')')

        rating_ranks_container = soup.find('div', class_='rating-ranks')
        rating_ranks = rating_ranks_container.find_all('a')

        global_rank = rating_ranks[0].strong.text
        country_rank = rating_ranks[1].strong.text

        if global_rank != 'NA' and global_rank != 'Inactive':
            global_rank = int(global_rank)
            country_rank = int(country_rank)

        def contests_details_get():
            rating_table = soup.find('table', class_='rating-table')
            if not rating_table:
                return []
            rating_table_rows = rating_table.find_all('td')

            '''Can add ranking url to contests'''

            try:
                long_challenge = {'name': 'Long Challenge', 'rating': int(rating_table_rows[1].text),
                                  'global_rank': int(rating_table_rows[2].a.hx.text),
                                  'country_rank': int(rating_table_rows[3].a.hx.text)}

            except ValueError:
                long_challenge = {'name': 'Long Challenge', 'rating': int(rating_table_rows[1].text),
                                  'global_rank': rating_table_rows[2].a.hx.text,
                                  'country_rank': rating_table_rows[3].a.hx.text}

            try:
                cook_off = {'name': 'Cook-off',
                            'rating': int(rating_table_rows[5].text),
                            'global_rank': int(rating_table_rows[6].a.hx.text),
                            'country_rank': int(rating_table_rows[7].a.hx.text)}
            except ValueError:
                cook_off = {'name': 'Cook-off',
                            'rating': int(rating_table_rows[5].text),
                            'global_rank': rating_table_rows[6].a.hx.text,
                            'country_rank': rating_table_rows[7].a.hx.text}

            try:
                lunch_time = {'name': 'Lunch Time', 'rating': int(rating_table_rows[9].text),
                              'global_rank': int(rating_table_rows[10].a.hx.text),
                              'country_rank': int(rating_table_rows[11].a.hx.text)}

            except ValueError:
                lunch_time = {'name': 'Lunch Time', 'rating': int(rating_table_rows[9].text),
                              'global_rank': rating_table_rows[10].a.hx.text,
                              'country_rank': rating_table_rows[11].a.hx.text}

            return [long_challenge, cook_off, lunch_time]

        def contest_rating_details_get():
            start_ind = page.text.find('[', page.text.find('all_rating'))
            end_ind = page.text.find(']', start_ind) + 1

            next_opening_brack = page.text.find('[', start_ind + 1)
            while next_opening_brack < end_ind:
                end_ind = page.text.find(']', end_ind + 1) + 1
                next_opening_brack = page.text.find('[', next_opening_brack + 1)

            all_rating = json.loads(page.text[start_ind: end_ind])
            for rating_contest in all_rating:
                rating_contest.pop('color')

            return all_rating

        def problems_solved_get():
            problem_solved_section = soup.find('section', class_='rating-data-section problems-solved')

            no_solved = problem_solved_section.find_all('h5')

            categories = problem_solved_section.find_all('article')

            fully_solved = {'count': int(re.findall(r'\d+', no_solved[0].text)[0])}

            if fully_solved['count'] != 0:
                for category in categories[0].find_all('p'):
                    category_name = category.find('strong').text[:-1]
                    fully_solved[category_name] = []

                    for prob in category.find_all('a'):
                        fully_solved[category_name].append({'name': prob.text,
                                                            'link': 'https://www.codechef.com' + prob['href']})

            partially_solved = {'count': int(re.findall(r'\d+', no_solved[1].text)[0])}
            if partially_solved['count'] != 0:
                for category in categories[1].find_all('p'):
                    category_name = category.find('strong').text[:-1]
                    partially_solved[category_name] = []

                    for prob in category.find_all('a'):
                        partially_solved[category_name].append({'name': prob.text,
                                                                'link': 'https://www.codechef.com' + prob['href']})

            return fully_solved, partially_solved

        def user_details_get():
            user_details_attribute_exclusion_list = {'username', 'link', 'teams list', 'discuss profile'}

            header_containers = soup.find_all('header')
            name = header_containers[1].find('h1', class_="h2-style").text

            user_details_section = soup.find('section', class_='user-details')
            user_details_list = user_details_section.find_all('li')

            user_details_response = {'name': name, 'username': user_details_list[0].text.split('★')[-1].rstrip('\n')}
            for user_details in user_details_list:
                attribute, value = user_details.text.split(':')[:2]
                attribute = attribute.strip().lower()
                value = value.strip()

                if attribute not in user_details_attribute_exclusion_list:
                    user_details_response[attribute] = value

            return user_details_response

        full, partial = problems_solved_get()
        details = {'status': 'Success', 'rating': int(rating), 'stars': stars, 'highest_rating': int(highest_rating),
                   'global_rank': global_rank, 'country_rank': country_rank,
                   'user_details': user_details_get(), 'contests': contests_details_get(),
                   'contest_ratings': contest_rating_details_get(), 'fully_solved': full, 'partially_solved': partial}

        return details

    def __codeforces(self):
        urls = {
            "user_info": {"url": f'https://codeforces.com/api/user.info?handles={self.__username}'},
            "user_contests": {"url": f'https://codeforces.com/contests/with/{self.__username}'}
        }

        reqs = [grequests.get(item["url"]) for item in urls.values() if item.get("url")]

        responses = grequests.map(reqs)

        details_api = {}
        contests = []
        for page in responses:
            if page.status_code != 200:
                raise UsernameError('User not Found')
            if page.request.url == urls["user_info"]["url"]:
                details_api = page.json()
            elif page.request.url == urls["user_contests"]["url"]:
                soup = BeautifulSoup(page.text, 'html.parser')
                table = soup.find('table', attrs={'class': 'user-contests-table'})
                table_body = table.find('tbody')

                rows = table_body.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    contests.append({
                        "Contest": cols[1],
                        "Rank": cols[3],
                        "Solved": cols[4],
                        "Rating Change": cols[5],
                        "New Rating": cols[6]
                    })

        if details_api.get('status') != 'OK':
            raise UsernameError('User not Found')

        details_api = details_api['result'][0]

        try:
            rating = details_api['rating']
            max_rating = details_api['maxRating']
            rank = details_api['rank']
            max_rank = details_api['maxRank']

        except KeyError:
            rating = 'Unrated'
            max_rating = 'Unrated'
            rank = 'Unrated'
            max_rank = 'Unrated'

        return {
            'status': 'Success',
            'username': self.__username,
            'platform': 'Codeforces',
            'rating': rating,
            'max rating': max_rating,
            'rank': rank,
            'max rank': max_rank,
            'contests': contests
        }

    def __spoj(self):
        url = 'https://www.spoj.com/users/{}/'.format(self.__username)

        page = requests.get(url)

        soup = BeautifulSoup(page.text, 'html.parser')
        details_container = soup.find_all('p')

        points = details_container[2].text.split()[3][1:]
        rank = details_container[2].text.split()[2][1:]
        join_date = details_container[1].text.split()[1] + ' ' + details_container[1].text.split()[2]
        institute = ' '.join(details_container[3].text.split()[1:])

        try:
            points = float(points)

        except ValueError:
            raise UsernameError('User not Found')

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
                   'points': float(points), 'rank': int(rank), 'solved': get_solved_problems(),
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
                   'rank': int(details_container[0].find('div', class_='txt').text),
                   'score': int(details_container[1].find('div', class_='txt').text),
                   'streak': details_container[2].find('div', class_='txt').text}

        return details

    def __atcoder(self):
        url = "https://atcoder.jp/users/{}".format(self.__username)

        page = requests.get(url)

        if page.status_code != 200:
            raise UsernameError("User not Found")

        soup = BeautifulSoup(page.text, "html.parser")
        tables = soup.find_all("table", class_="dl-table")
        if len(tables) < 2:
            details = {
                "status": "Success",
                "username": self.__username,
                "platform": "Atcoder",
                "rating": "NA",
                "highest": "NA",
                "rank": "NA",
                "level": "NA",
            }
            return details
        rows = tables[1].find_all("td")
        try:
            rank = int(rows[0].text[:-2])
            current_rating = int(rows[1].text)
            spans = rows[2].find_all("span")
            highest_rating = int(spans[0].text)
            level = spans[2].text
        except Exception as E:
            raise BrokenChangesError(E)
        details = {
            "status": "Success",
            "username": self.__username,
            "platform": "Atcoder",
            "rating": current_rating,
            "highest": highest_rating,
            "rank": rank,
            "level": level,
        }
        return details

    # DEPRECATED
    def __leetcode(self):
        url = 'https://leetcode.com/{}'.format(self.__username)

        if requests.get(url).status_code != 200:
            raise UsernameError('User not Found')

        options = webdriver.ChromeOptions()
        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        # driver = webdriver.PhantomJS(executable_path='./phantomjs')

        driver = webdriver.Chrome(options=options, executable_path=os.environ.get("CHROMEDRIVER_PATH"))
        try:
            driver.get(url)

            driver.implicitly_wait(10)

            hover_ranking = driver.find_element_by_xpath(
                '/html/body/div[1]/div[2]/div/div[1]/div[1]/div[2]/div/div[1]/div[3]/div')
            ActionChains(driver).move_to_element(to_element=hover_ranking).perform()

            ranking = driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div[2]').text
            print('rank: ', ranking)

            total_problems_solved = driver.find_element_by_xpath(
                '/html/body/div[1]/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div[2]').text

            acceptance_rate_span_1 = driver.find_element_by_xpath(
                '/html/body/div[1]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/span[1]').text
            acceptance_rate_span_2 = driver.find_element_by_xpath(
                '/html/body/div[1]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/span[2]').text
            acceptance_rate = str(acceptance_rate_span_1) + str(acceptance_rate_span_2)

            easy_questions_solved = driver.find_element_by_xpath(
                '//*[@id="profile-root"]/div[2]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/span[1]').text
            total_easy_questions = driver.find_element_by_xpath(
                '//*[@id="profile-root"]/div[2]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/span[2]').text

            medium_questions_solved = driver.find_element_by_xpath(
                '//*[@id="profile-root"]/div[2]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/span[1]').text
            total_medium_questions = driver.find_element_by_xpath(
                '//*[@id="profile-root"]/div[2]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/span[2]').text

            hard_questions_solved = driver.find_element_by_xpath(
                '//*[@id="profile-root"]/div[2]/div/div[1]/div[2]/div/div[2]/div/div[3]/div[2]/span[1]').text
            total_hard_questions = driver.find_element_by_xpath(
                '//*[@id="profile-root"]/div[2]/div/div[1]/div[2]/div/div[2]/div/div[3]/div[2]/span[2]').text

            contribution_points = driver.find_element_by_xpath(
                '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div/div/div/li[1]/span').text

            contribution_problems = driver.find_element_by_xpath(
                '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div/div/div/li[2]/span').text

            contribution_testcases = driver.find_element_by_xpath(
                '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div/div/div/li[3]/span').text

            reputation = driver.find_element_by_xpath(
                '/html/body/div[1]/div[2]/div/div[1]/div[4]/div[2]/div/div/div/li/span').text
        finally:
            driver.close()
            driver.quit()

        details = {'status': 'Success', 'ranking': ranking[9:],
                   'total_problems_solved': total_problems_solved,
                   'acceptance_rate': acceptance_rate,
                   'easy_questions_solved': easy_questions_solved,
                   'total_easy_questions': total_easy_questions,
                   'medium_questions_solved': medium_questions_solved,
                   'total_medium_questions': total_medium_questions,
                   'hard_questions_solved': hard_questions_solved,
                   'total_hard_questions': total_hard_questions,
                   'contribution_points': contribution_points,
                   'contribution_problems': contribution_problems,
                   'contribution_testcases': contribution_testcases,
                   'reputation': reputation}

        return details

    def __leetcode_v2(self):

        def __parse_response(response):
            total_submissions_count = 0
            total_easy_submissions_count = 0
            total_medium_submissions_count = 0
            total_hard_submissions_count = 0

            ac_submissions_count = 0
            ac_easy_submissions_count = 0
            ac_medium_submissions_count = 0
            ac_hard_submissions_count = 0

            total_easy_questions = 0
            total_medium_questions = 0
            total_hard_questions = 0

            total_problems_solved = 0
            easy_questions_solved = 0
            medium_questions_solved = 0
            hard_questions_solved = 0

            acceptance_rate = 0
            easy_acceptance_rate = 0
            medium_acceptance_rate = 0
            hard_acceptance_rate = 0

            total_problems_submitted = 0
            easy_problems_submitted = 0
            medium_problems_submitted = 0
            hard_problems_submitted = 0

            ranking = get_safe_nested_key(['data', 'matchedUser', 'profile', 'ranking'], response)
            if ranking > 100000:
                ranking = '~100000'

            reputation = get_safe_nested_key(['data', 'matchedUser', 'profile', 'reputation'], response)

            total_questions_stats = get_safe_nested_key(['data', 'allQuestionsCount'], response)
            for item in total_questions_stats:
                if item['difficulty'] == "Easy":
                    total_easy_questions = item['count']
                if item['difficulty'] == "Medium":
                    total_medium_questions = item['count']
                if item['difficulty'] == "Hard":
                    total_hard_questions = item['count']

            ac_submissions = get_safe_nested_key(['data', 'matchedUser', 'submitStats', 'acSubmissionNum'], response)
            for submission in ac_submissions:
                if submission['difficulty'] == "All":
                    total_problems_solved = submission['count']
                    ac_submissions_count = submission['submissions']
                if submission['difficulty'] == "Easy":
                    easy_questions_solved = submission['count']
                    ac_easy_submissions_count = submission['submissions']
                if submission['difficulty'] == "Medium":
                    medium_questions_solved = submission['count']
                    ac_medium_submissions_count = submission['submissions']
                if submission['difficulty'] == "Hard":
                    hard_questions_solved = submission['count']
                    ac_hard_submissions_count = submission['submissions']

            total_submissions = get_safe_nested_key(['data', 'matchedUser', 'submitStats', 'totalSubmissionNum'],
                                                    response)
            for submission in total_submissions:
                if submission['difficulty'] == "All":
                    total_problems_submitted = submission['count']
                    total_submissions_count = submission['submissions']
                if submission['difficulty'] == "Easy":
                    easy_problems_submitted = submission['count']
                    total_easy_submissions_count = submission['submissions']
                if submission['difficulty'] == "Medium":
                    medium_problems_submitted = submission['count']
                    total_medium_submissions_count = submission['submissions']
                if submission['difficulty'] == "Hard":
                    hard_problems_submitted = submission['count']
                    total_hard_submissions_count = submission['submissions']

            if total_submissions_count > 0:
                acceptance_rate = round(ac_submissions_count * 100 / total_submissions_count, 2)
            if total_easy_submissions_count > 0:
                easy_acceptance_rate = round(ac_easy_submissions_count * 100 / total_easy_submissions_count, 2)
            if total_medium_submissions_count > 0:
                medium_acceptance_rate = round(ac_medium_submissions_count * 100 / total_medium_submissions_count, 2)
            if total_hard_submissions_count > 0:
                hard_acceptance_rate = round(ac_hard_submissions_count * 100 / total_hard_submissions_count, 2)

            contribution_points = get_safe_nested_key(['data', 'matchedUser', 'contributions', 'points'],
                                                      response)
            contribution_problems = get_safe_nested_key(['data', 'matchedUser', 'contributions', 'questionCount'],
                                                        response)
            contribution_testcases = get_safe_nested_key(['data', 'matchedUser', 'contributions', 'testcaseCount'],
                                                         response)

            return {
                'status': 'Success',
                'ranking': str(ranking),
                'total_problems_submitted': str(total_problems_submitted),
                'total_problems_solved': str(total_problems_solved),
                'acceptance_rate': f"{acceptance_rate}%",
                'easy_problems_submitted': str(easy_problems_submitted),
                'easy_questions_solved': str(easy_questions_solved),
                'easy_acceptance_rate': f"{easy_acceptance_rate}%",
                'total_easy_questions': str(total_easy_questions),
                'medium_problems_submitted': str(medium_problems_submitted),
                'medium_questions_solved': str(medium_questions_solved),
                'medium_acceptance_rate': f"{medium_acceptance_rate}%",
                'total_medium_questions': str(total_medium_questions),
                'hard_problems_submitted': str(hard_problems_submitted),
                'hard_questions_solved': str(hard_questions_solved),
                'hard_acceptance_rate': f"{hard_acceptance_rate}%",
                'total_hard_questions': str(total_hard_questions),
                'contribution_points': str(contribution_points),
                'contribution_problems': str(contribution_problems),
                'contribution_testcases': str(contribution_testcases),
                'reputation': str(reputation)
            }

        url = f'https://leetcode.com/{self.__username}'
        if requests.get(url).status_code != 200:
            raise UsernameError('User not Found')
        payload = {
            "operationName": "getUserProfile",
            "variables": {
                "username": self.__username
            },
            "query": "query getUserProfile($username: String!) {  allQuestionsCount {    difficulty    count  }  matchedUser(username: $username) {    contributions {    points      questionCount      testcaseCount    }    profile {    reputation      ranking    }    submitStats {      acSubmissionNum {        difficulty        count        submissions      }      totalSubmissionNum {        difficulty        count        submissions      }    }  }}"
        }
        res = requests.post(url='https://leetcode.com/graphql',
                            json=payload,
                            headers={'referer': f'https://leetcode.com/{self.__username}/'})
        res.raise_for_status()
        res = res.json()
        return __parse_response(res)

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

        if platform == 'leetcode':
            return self.__leetcode_v2()

        if platform == 'atcoder':
            return self.__atcoder()

        raise PlatformError('Platform not Found')


if __name__ == '__main__':
    ud = UserData('uwi')
    ans = ud.get_details('leetcode')

    print(ans)

    # leetcode backward compatibility test. Commenting it out as it will fail in future
    # leetcode_ud = UserData('saurabhprakash')
    # leetcode_ans = leetcode_ud.get_details('leetcode')
    # assert leetcode_ans == dict(status='Success', ranking='~100000', total_problems_solved='10',
    #                             acceptance_rate='56.0%', easy_questions_solved='3', total_easy_questions='457',
    #                             medium_questions_solved='5', total_medium_questions='901', hard_questions_solved='2',
    #                             total_hard_questions='365', contribution_points='58', contribution_problems='0',
    #                             contribution_testcases='0', reputation='0')

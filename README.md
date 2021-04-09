# Competitive_Programming_Score_API
A REST API to get user details for competitive coding platforms - Codeforces, Codechef, SPOJ, Interviewbit

## Base URL
https://competitive-coding-api.herokuapp.com/api/

## Request Format
https://competitive-coding-api.herokuapp.com/api/{platform_name}/{user_name}

### Example URL
https://competitive-coding-api.herokuapp.com/api/codechef/abhijeet_ar

### Example Badges
[Shields](https://shields.io/) can create dynamically updated badges from a JSON source such as this API. More configuration options are also available in their section on [dynamic badges](https://shields.io/#dynamic-badge).

Replace `<USERNAME>` with your username on that platform.

#### <a href="https://codeforces.com/profile/abhijeet_ar"><img src="https://img.shields.io/badge/dynamic/json?&color=1f8acb&logo=codeforces&label=Codeforces&url=https://competitive-coding-api.herokuapp.com/api/codeforces/abhijeet_ar&query=%24.rating&prefix=Rating%20&style=for-the-badge&cacheSeconds=259200" alt="abhijeet_ar's profile on Codeforces" title="abhijeet_ar's profile on Codeforces"></a>
`https://img.shields.io/badge/dynamic/json?&color=1f8acb&logo=codeforces&label=Codeforces&url=https://competitive-coding-api.herokuapp.com/api/codeforces/<USERNAME>&query=%24.<FIELD>&prefix=<TEXT>&style=for-the-badge&cacheSeconds=86400`

Suggested use,
* `<FIELD>` = `rating`
* `<TEXT>` = `Rating%20`

#### <a href="https://www.codechef.com/users/radix28_numb"><img src="https://img.shields.io/badge/dynamic/json?label=CodeChef&query=%24.country_rank&url=https://competitive-coding-api.herokuapp.com/api/codechef/radix28_numb&prefix=US%20%23&logo=codechef&logoColor=f5f5dc&labelColor=7b5e47&style=for-the-badge&cacheSeconds=259200" alt="radix28_numb's profile on CodeChef" title="radix28_numb's profile on CodeChef"></a>
`https://img.shields.io/badge/dynamic/json?label=CodeChef&query=%24.global_rank&url=https://competitive-coding-api.herokuapp.com/api/codechef/<USERNAME>&prefix=<TEXT>&logo=codechef&logoColor=f5f5dc&labelColor=7b5e47&style=for-the-badge&cacheSeconds=86400`

Suggested use,
* `<FIELD>` = `global_rank`, `country_rank` or `rating`
* `<TEXT>` = `Rank%20`, country abbreviation (e.g., `US%20%23`) or `Rating%20`

### Pro Tip 💡
Use this [JSON Formatter Chrome Extension](https://chrome.google.com/webstore/detail/json-formatter/bcjindcccaagfpapjjmafapmmgkkhgoa?hl=en) to view in a structured format.

## Platforms Available 
* Codeforces
* Codechef
* SPOJ
* Interviewbit
* Leetcode (new)
* Atcoder

If you would like to leave a feedback or request a feature, please [open an issue](https://github.com/Abhijeet-AR/Competitive_Programming_Score_API/issues) or feel free to PR. Do follow [these](https://help.github.com/articles/creating-a-pull-request/) instructions to make a valid PR.

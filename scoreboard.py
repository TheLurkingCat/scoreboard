"""
LICENSE: MIT license

This module can help us know about who can ask when
we have troubles in some buggy codes while solving problems.

"""

from configparser import ConfigParser
from datetime import datetime
from json import dumps, loads
from time import mktime, sleep

from matplotlib.pyplot import savefig, show, subplots
from pandas import DataFrame, read_html, read_pickle
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Scoreboard:
    """Handles a dataframe to build up a scoreboard.

    Attributes:
        problems: (list) A list of problem id which we are tracking.
        scoreboard: (Dataframe) A pandas.Dataframe that saves AC attempt
                    by student id.
        crawler: (Crawler) A web crawler to fetch data.
        size: (int) The columns we need to initialize a student's score.
        pickle_name: (str) The filename of where pickle save.
        html_name: (str) The filename of where html file save.
    """

    def __init__(self, problems, debug, pickle_name, html_name):
        self.problems = problems
        self.scoreboard = DataFrame(columns=problems + ["Total"])
        self.scoreboard.index.name = "Student_ID"
        self.crawler = Crawler(headless=(not debug))
        self.size = len(problems)
        self.pickle_name = pickle_name
        self.html_name = html_name

    def update(self):
        """Update scoreboard using web crawler.

        Since crawler can return a Dataframe, we can use it to update scoreboard.
        """
        for problem_id in self.problems:
            verdict_table = self.crawler.get_submit(problem_id)
            for i in range(len(verdict_table)):
                student_id = verdict_table.iloc[i]["Submitter"]
                verdict = verdict_table.iloc[i]["Verdict"]
                try:
                    student = self.scoreboard.loc[student_id]
                except KeyError:
                    self.scoreboard.loc[student_id] = [
                        "Not Attempted"] * self.size + [0]
                    student = self.scoreboard.loc[student_id]
                if verdict == "AC":
                    if student[problem_id] != "AC":
                        student[problem_id] = "AC"
                        student["Total"] += 1

                elif student[problem_id] == "Not Attempted":
                    student[problem_id] = "Attempted"

        self.scoreboard.sort_values(
            by=["Total", "Student_ID"], inplace=True, ascending=[False, True])

    def visualize(self):
        """
        Make scoreboard picture using matplotlib
        """
        def hightlight(scoreboard):
            color_list = []
            for x in scoreboard:
                if x == "AC":
                    color_list.append("background-color: green")
                elif x == "Attempted":
                    color_list.append("background-color: red")
                else:
                    color_list.append("background-color: gray")
            return color_list

        scoreboard = self.scoreboard.drop(columns=["Total"])

        with open(self.html_name, 'w') as f:
            f.write(scoreboard.style.apply(hightlight).render())

    def save_data(self):
        self.scoreboard.to_pickle(self.pickle_name)

    def load_data(self):
        self.scoreboard = read_pickle(self.pickle_name)


class Crawler:
    """Handles webdriver to crawl data.

    Attributes:
        driver: (Chrome) A selenium.webdriver.Chrome to automatically
                control Chrome browser.
    """

    def __init__(self, headless=True):
        option = ChromeOptions()
        if headless:
            option.add_argument('headless')
        self.driver = Chrome(options=option)
        self.url = "https://oj.nctu.me/groups/11/submissions/?count=10000&page=1&problem_id={}"
        self.set_cookies()

    def set_cookies(self):
        """We need cookies to Access OJ.

        We need to dump cookie so you need to log in to Formosa OJ
        then copy the cookie's data to access without logged in everytime.
        """
        self.driver.delete_all_cookies()
        self.driver.get("https://oj.nctu.me")
        with open("token.json", "r") as cookie:
            self.driver.add_cookie(loads(cookie.read()))

    def get_submit(self, problem_id):
        """Get html from submission page.

        Get the html source of the page and it can parse to pandas.

        Args:
            problem_id: (int) The id of the problem we are looking at.

        Returns:
            (Dataframe) A Dataframe consist a column of student id.
        """
        self.driver.get(self.url.format(problem_id))

        WebDriverWait(self.driver, 10, 0.5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-responsive")))

        accept = read_html(self.driver.page_source, converters={
            'Submitter': str, "Verdict": str})
        accept = accept[0][["Submitter", "Verdict"]]

        while accept.isnull().values.any():
            sleep(1)
            accept = read_html(self.driver.page_source, converters={
                'Submitter': str, "Verdict": str})
            accept = accept[0][["Submitter", "Verdict"]]

        return accept[accept["Submitter"].str.match(r"(\d){7}")]


def main(config):
    """Main function here."""
    scoreboard = Scoreboard(
        [int(x) for x in config["problems"].split()], config["debug"] == "yes", config["data"], config["web_page"])

    scoreboard.update()
    scoreboard.visualize()
    # scoreboard.save_data()


if __name__ == "__main__":
    CONFIG = ConfigParser()
    CONFIG.read("settings.ini")
    main(CONFIG["DEFAULT"])

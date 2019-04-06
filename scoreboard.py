"""
LICENSE: MIT license

This module can help us know about who can ask when
we have troubles in some buggy codes while solving problems.

"""

from json import loads
from time import sleep

from pandas import DataFrame, read_html
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
    """

    def __init__(self, *problems):
        self.problems = problems
        self.scoreboard = DataFrame(columns=problems+["Total"])
        self.crawler = Crawler()
        self.size = len(problems)

    def update(self):
        """Update scoreboard using web crawler.

        Since crawler can return a html string, we can parse it to pandas
        then update each student's score.
        """
        for problem_id in self.problems:
            source = self.crawler.get_accept_submit(problem_id)

            accept_table = read_html(source, converters={'Submitter': str})[0]

            for student_id in set(*zip(*accept_table[["Submitter"]].values)):
                try:
                    student = self.scoreboard.loc[student_id]
                except KeyError:
                    self.scoreboard.loc[student_id] = [
                        "Unsolved"] * self.size + [0]
                    student = self.scoreboard.loc[student_id]
                student[problem_id] = "AC"
                student["Total"] += 1
        self.scoreboard.sort_values(by=["Total"])

    def __str__(self):
        """
        This is just a simple debug printer.
        TODO: pretty print
        """
        return str(self.scoreboard)


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

    def get_accept_submit(self, problem_id):
        """Get html from submission page.

        Get the html source of the page and it can parse to pandas.

        Args:
            problem_id: (int) The id of the problem we are looking at.

        Returns:
            (str) A html source string.
        """
        self.driver.get(
            "https://oj.nctu.me/groups/11/submissions\
            / ?count=10000&page=1&problem_id={}&verdict_id=10".format(problem_id))

        WebDriverWait(self.driver, 10, 0.5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-responsive")))
        sleep(10)
        return self.driver.page_source


def main():
    """Main function here."""
    scoreboard = Scoreboard(819, 820, 822, 823, 825, 826, 829, 830)
    scoreboard.update()
    print(scoreboard)


if __name__ == "__main__":
    main()

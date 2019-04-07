"""
LICENSE: MIT license

This module can help us know about who can ask when
we have troubles in some buggy codes while solving problems.

"""

from json import loads
from time import sleep

from matplotlib.pyplot import figure, savefig, show, subplots
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

    def __init__(self, problems, debug=False):
        self.problems = problems
        self.scoreboard = DataFrame(columns=problems + ["Total"])
        self.scoreboard.index.name = "Student_ID"
        self.crawler = Crawler(headless=(not debug))
        self.size = len(problems)

    def update(self):
        """Update scoreboard using web crawler.

        Since crawler can return a Dataframe, we can use it to update scoreboard.
        """
        for problem_id in self.problems:
            accept_table = self.crawler.get_accept_submit(problem_id)

            for student_id in set(accept_table.values.flatten()):
                try:
                    student = self.scoreboard.loc[student_id]
                except KeyError:
                    self.scoreboard.loc[student_id] = [
                        "Unsolved"] * self.size + [0]
                    student = self.scoreboard.loc[student_id]
                student[problem_id] = "AC"
                student["Total"] += 1
        self.scoreboard.sort_values(
            by=["Total", "Student_ID"], inplace=True, ascending=[False, True])

    def visualize(self, filename=None):
        """
        Make scoreboard picture using matplotlib

        Args:
            filename: (str) A image like filename, the picture will show on screen
                      if filename is not given.
        """
        scoreboard = self.scoreboard.drop(columns=["Total"])
        color = scoreboard.copy()

        n_rows, n_columns = len(scoreboard) + 1, len(scoreboard.columns) + 1

        _, graph = subplots(figsize=(n_columns * 0.2 + 1.5, n_rows * 0.2))

        color[color == "AC"] = "#00FF00"
        color[color == "Unsolved"] = "#FF0000"

        graph.axis('off')

        graph.table(loc='center', cellLoc="center", rowLoc="center",
                    colWidths=[0.2]*n_columns, cellColours=color.values,
                    cellText=scoreboard.values, colLabels=scoreboard.columns,
                    rowLabels=scoreboard.index)

        if filename is None:
            show()
        else:
            savefig(filename)


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
        self.url = "https://oj.nctu.me/groups/11/submissions/?count=10000&page=1&problem_id={}&verdict_id=10"
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
            (Dataframe) A Dataframe consist a column of student id.
        """
        self.driver.get(self.url.format(problem_id))

        WebDriverWait(self.driver, 10, 0.5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-responsive")))

        accept = read_html(self.driver.page_source, converters={
                           'Submitter': str})[0][["Submitter"]]

        while accept.isnull().values.any():
            sleep(1)
            accept = read_html(self.driver.page_source, converters={
                'Submitter': str})[0][["Submitter"]]

        return accept


def main():
    """Main function here."""
    scoreboard = Scoreboard([819, 820, 822, 823, 825, 826, 829, 830])
    scoreboard.update()
    scoreboard.visualize("scoreboard.png")


if __name__ == "__main__":
    main()

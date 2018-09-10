#!/usr/bin/env python3

# pylint:disable=line-too-long
"""
The tool to check domains or IP availability.

::


    :::::::::  :::   ::: :::::::::: :::    ::: ::::    :::  ::::::::  :::::::::: :::::::::  :::        ::::::::::
    :+:    :+: :+:   :+: :+:        :+:    :+: :+:+:   :+: :+:    :+: :+:        :+:    :+: :+:        :+:
    +:+    +:+  +:+ +:+  +:+        +:+    +:+ :+:+:+  +:+ +:+        +:+        +:+    +:+ +:+        +:+
    +#++:++#+    +#++:   :#::+::#   +#+    +:+ +#+ +:+ +#+ +#+        +#++:++#   +#++:++#+  +#+        +#++:++#
    +#+           +#+    +#+        +#+    +#+ +#+  +#+#+# +#+        +#+        +#+    +#+ +#+        +#+
    #+#           #+#    #+#        #+#    #+# #+#   #+#+# #+#    #+# #+#        #+#    #+# #+#        #+#
    ###           ###    ###         ########  ###    ####  ########  ########## #########  ########## ##########

This submodule will provide the exipration date logic.

Author:
    Nissar Chababy, @funilrys, contactTATAfunilrysTODTODcom

Special thanks:
    https://pyfunceble.readthedocs.io/en/dev/special-thanks.html

Contributors:
    http://pyfunceble.readthedocs.io/en/dev/special-thanks.html

Project link:
    https://github.com/funilrys/PyFunceble

Project documentation:
    https://pyfunceble.readthedocs.io

Project homepage:
    https://funilrys.github.io/PyFunceble/

License:
::


    MIT License

    Copyright (c) 2017-2018 Nissar Chababy

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
# pylint: enable=line-too-long
# pylint: disable=bad-continuation
import PyFunceble
from PyFunceble import requests
from PyFunceble.generate import Generate
from PyFunceble.helpers import Dict, File, Regex
from PyFunceble.http_code import HTTPCode
from PyFunceble.lookup import Lookup
from PyFunceble.referer import Referer
from PyFunceble.status import Status


class ExpirationDate:
    """
    Get, format and return the epiration date of a domain if exist.
    """

    def __init__(self):
        # We set the log separator.
        self.log_separator = "=" * 100 + " \n"

        # We initiate a variable which will save the extracted expiration date.
        self.expiration_date = ""

        # We initate a variable which will save our WHOIS record.s
        self.whois_record = ""

    @classmethod
    def psl_db(cls):
        """
        Convert `public_suffix.json` to a dictionnary.
        """

        # We construct the file path to read.
        file_to_read = (
            PyFunceble.CURRENT_DIRECTORY
            + PyFunceble.OUTPUTS["default_files"]["public_suffix"]
        )

        # * We read, convert to dict and return the file content.
        # and
        # * We fill the database.
        PyFunceble.CONFIGURATION["psl_db"].update(
            Dict().from_json(File(file_to_read).read())
        )

    @classmethod
    def is_domain_valid(cls, domain=None):
        """
        Check if PyFunceble.CONFIGURATION['domain'] is a valid domain.

        Argument:
            - domain: str
                The domain to test

        """

        if PyFunceble.CONFIGURATION["psl_db"] == {}:
            # The psl database is empty.

            # We fill it.
            cls.psl_db()

        # We initate our regex which will match for valid domains.
        regex_valid_domains = r"^(?=.{0,253}$)(([a-z0-9][a-z0-9-]{0,61}[a-z0-9]|[a-z0-9])\.)+((?=.*[^0-9])([a-z0-9][a-z0-9-]{0,61}[a-z0-9]|[a-z0-9]))$"  # pylint: disable=line-too-long

        # We initiate our regex which will match for valid subdomains.
        regex_valid_subdomains = r"^(?=.{0,253}$)(([a-z0-9_][a-z0-9-_]{0,61}[a-z0-9_-]|[a-z0-9])\.)+((?=.*[^0-9])([a-z0-9][a-z0-9-]{0,61}[a-z0-9]|[a-z0-9]))$"  # pylint: disable=line-too-long

        if domain:
            # A domain is given.

            # We set the element to test as the parsed domain.
            to_test = domain
        else:
            # A domain is not given.

            # We set the element to test as the currently tested element.
            to_test = PyFunceble.CONFIGURATION["domain"]

        if Regex(to_test, regex_valid_domains, return_data=False).match():
            # The element pass the domain validation.

            # We return True. The domain is valid.
            return True

        # The element did not pass the domain validation. That means that it has invalid character
        # or the position of - or _ are not right.

        try:
            # We get the position of the last point.
            last_point_index = to_test.rindex(".")
            # And with the help of the position of the last point, we get the domain extension.
            extension = to_test[last_point_index + 1 :]

            if extension in PyFunceble.CONFIGURATION["psl_db"]:
                # The extension is into the psl database.

                for suffix in PyFunceble.CONFIGURATION["psl_db"][extension]:
                    # We loop through the element of the extension into the psl database.

                    try:
                        # We try to get the position of the currently read suffix
                        # in the element ot test.
                        suffix_index = to_test.rindex("." + suffix)

                        # We get the element to check.
                        # The idea here is to delete the suffix, then retest with our
                        # subdomains regex.
                        to_check = to_test[:suffix_index]

                        if "." in to_check:
                            # There is a point into the new element to check.

                            # We check if it passes our subdomain regex.
                            # * True: It's a valid domain.
                            # * False: It's an invalid domain.
                            return Regex(
                                to_check, regex_valid_subdomains, return_data=False
                            ).match()

                    except ValueError:
                        # In case of a value error because the position is not found,
                        # we continue to the next element.
                        pass

            # * The extension is not into the psl database.
            # or
            # * there was no point into the suffix checking.

            # We get the element before the last point.
            to_check = to_test[:last_point_index]

            if "." in to_check:
                # There is a point in to_check

                # We check if it passes our subdomain regex.
                # * True: It's a valid domain.
                # * False: It's an invalid domain.
                return Regex(
                    to_check, regex_valid_subdomains, return_data=False
                ).match()

        except (ValueError, AttributeError):
            # In case of a value or attribute error we ignore them.
            pass

        # And we return False, the domain is not valid.
        return False

    @classmethod
    def is_ip_valid(cls, ip_to_check=None):
        """
        Check if PyFunceble.CONFIGURATION['domain'] is a valid IPv4.

        Argument:
            - ip_to_check: str
                The ip to test

        Note:
            We only test IPv4 because for now we only support domain and IPv4.
        """

        # We initate our regex which will match for valid IPv4.
        regex_ipv4 = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[0-9]{1,}\/[0-9]{1,})$"  # pylint: disable=line-too-long

        if ip_to_check:
            # An element is localy given.

            # We consider it as the element to test.
            to_test = ip_to_check
        else:
            # An element is not localy given.

            # We consider the global element to test as the element to test.
            to_test = PyFunceble.CONFIGURATION["domain"]

        # We check if it passes our IPv4 regex.
        # * True: It's a valid IPv4.
        # * False: It's an invalid IPv4.
        return Regex(to_test, regex_ipv4, return_data=False).match()

    def get(self):  # pragma: no cover
        """
        Execute the logic behind the meaning of ExpirationDate + return the matched status.
        """

        # We get the status of the domain validation.
        domain_validation = self.is_domain_valid()
        # We get the status of the IPv4 validation.
        ip_validation = self.is_ip_valid()

        if domain_validation and not ip_validation or domain_validation:
            # * The element is a valid domain.
            # and
            # * The element is not ahe valid IPv4.
            # or
            # * The element is a valid domain.

            # * We get the HTTP status code of the currently tested element.
            # and
            # * We try to get the element status from the IANA database.
            PyFunceble.CONFIGURATION.update(
                {"http_code": HTTPCode().get(), "referer": Referer().get()}
            )

            if PyFunceble.CONFIGURATION["referer"] in [
                PyFunceble.STATUS["official"]["up"],
                PyFunceble.STATUS["official"]["down"],
                PyFunceble.STATUS["official"]["invalid"],
            ]:
                # The WHOIS record status is into our list of official status.

                # We consider that status as the status of the tested element.
                return PyFunceble.CONFIGURATION["referer"]

            # The WHOIS record status is not into our list of official status.

            if PyFunceble.CONFIGURATION["referer"]:
                # The iana database comparison status is not None.

                # We try to extract the expiration date from the WHOIS record.
                # And we return the matched status.
                return self._extract()

            # The iana database comparison status is None.

            # We log our whois record if the debug mode is activated.
            self._whois_log()

            # And we return and handle the official down status.
            return Status(PyFunceble.STATUS["official"]["down"]).handle()

        if ip_validation and not domain_validation or ip_validation:
            # * The element is a valid IPv4.
            # and
            # * The element is not a valid domain.
            # or
            # * The element is a valid IPv4.

            # We get the HTTP status code.
            PyFunceble.CONFIGURATION["http_code"] = HTTPCode().get()

            # We log our whois record if the debug mode is activated.
            self._whois_log()

            # And we return and handle the official down status.
            return Status(PyFunceble.STATUS["official"]["down"]).handle()

        # The validation was not passed.

        # We log our whois record if the debug mode is activated.
        self._whois_log()

        # And we return and handle the official invalid status.
        return Status(PyFunceble.STATUS["official"]["invalid"]).handle()

    def _whois_log(self):  # pragma: no cover
        """
        Log the whois record into a file
        """

        if PyFunceble.CONFIGURATION["debug"] and PyFunceble.CONFIGURATION["logs"]:
            # The debug and the logs subsystem are activated.

            # We construct the log format
            log = (
                self.log_separator + str(self.whois_record) + "\n" + self.log_separator
            )

            # We construct the path to the file we have to create/write.
            output = PyFunceble.OUTPUT_DIRECTORY
            output += PyFunceble.OUTPUTS["parent_directory"]
            output += PyFunceble.OUTPUTS["logs"]["directories"]["parent"]
            output += PyFunceble.OUTPUTS["logs"]["directories"]["whois"]

            if PyFunceble.CONFIGURATION["referer"]:
                # The iana database comparison status is not equal to None.

                # We append the iana database comparison status to the output path.
                output += PyFunceble.CONFIGURATION["referer"]
            else:
                # The iana database comparison status is not equal to None.

                # We append the invalid status to the output path.
                output += PyFunceble.STATUS["official"]["invalid"]

            # And we finally write our whois record.
            File(output).write(log)

    @classmethod
    def _convert_1_to_2_digits(cls, number):
        """
        Convert 1 digit number to two digits.
        """

        return str(number).zfill(2)

    @classmethod
    def _convert_or_shorten_month(cls, data):
        """
        Convert a given month into our unified format.

        Argument:
            - data: str
                The month to convert or shorten.

        Returns: str
            The unified month name.
        """

        # We map the different month and their possible representation.
        short_month = {
            "jan": [str(1), "01", "Jan", "January"],
            "feb": [str(2), "02", "Feb", "February"],
            "mar": [str(3), "03", "Mar", "March"],
            "apr": [str(4), "04", "Apr", "April"],
            "may": [str(5), "05", "May"],
            "jun": [str(6), "06", "Jun", "June"],
            "jul": [str(7), "07", "Jul", "July"],
            "aug": [str(8), "08", "Aug", "August"],
            "sep": [str(9), "09", "Sep", "September"],
            "oct": [str(10), "Oct", "October"],
            "nov": [str(11), "Nov", "November"],
            "dec": [str(12), "Dec", "December"],
        }

        for month in short_month:
            # We loop through our map.

            if data in short_month[month]:
                # If the parsed data (or month if you prefer) is into our map.

                # We return the element (or key if you prefer) assigned to
                # the month.
                return month

        # The element is not into our map.

        # We return the parsed element (or month if you prefer).
        return data

    def log(self):  # pragma: no cover
        """
        Log the extracted expiration date and domain into a file.
        """

        if PyFunceble.CONFIGURATION["logs"]:
            # The logs subsystem is activated.

            # We construct our log format.
            log = self.log_separator + "Expiration Date: %s \n" % self.expiration_date
            log += "Tested domain: %s \n" % PyFunceble.CONFIGURATION["domain"]

            # And we write the log into the right location.
            File(
                PyFunceble.OUTPUT_DIRECTORY
                + PyFunceble.OUTPUTS["parent_directory"]
                + PyFunceble.OUTPUTS["logs"]["directories"]["parent"]
                + PyFunceble.OUTPUTS["logs"]["directories"]["date_format"]
                + PyFunceble.CONFIGURATION["referer"]
            ).write(log)

            if PyFunceble.CONFIGURATION["share_logs"]:
                # The logs sharing is activated.

                # We map the data we have to send.
                date_to_share = {
                    "domain": PyFunceble.CONFIGURATION["domain"],
                    "expiration_date": self.expiration_date,
                    "whois_server": PyFunceble.CONFIGURATION["referer"],
                }

                # And we share the logs with the api.
                requests.post(PyFunceble.LINKS["api_date_format"], data=date_to_share)

    def _cases_management(self, regex_number, matched_result):
        """
        A little helper of self.format. (Avoiding of nested loops)

        Note:
            Please note that the second value of the case represent the groups
            in order [day,month,year]. This means that a [2,1,0] will be for
            example for a date in format `2017-01-02` where `01` is the month.

        Retuns: list or None
            - None: the case is unknown.
            - list: the list representing the date [day, month, year]
        """

        # We map our regex numbers with with the right group order.
        # Note: please report to the method note for more information about the mapping.
        cases = {
            "first": [[1, 2, 3, 10, 11, 22, 26, 27, 28, 29, 32, 34, 38], [0, 1, 2]],
            "second": [[14, 15, 31, 33, 36, 37], [1, 0, 2]],
            "third": [
                [4, 5, 6, 7, 8, 9, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 30, 35],
                [2, 1, 0],
            ],
        }

        for case in cases:
            # We loop through the cases.

            # We get the case data.
            case_data = cases[case]

            if int(regex_number) in case_data[0]:
                # The regex number is into the currently read case data.

                # We return a list with the formated elements.
                # 1. We convert the day to 2 digits.
                # 2. We convert the month to the unified format.
                # 3. We return the year.
                return [
                    self._convert_1_to_2_digits(matched_result[case_data[1][0]]),
                    self._convert_or_shorten_month(matched_result[case_data[1][1]]),
                    str(matched_result[case_data[1][2]]),
                ]

        # The regex number is not already mapped.

        # We return the parsed data.
        return matched_result  # pragma: no cover

    def _format(self, date_to_convert=None):
        """
        Format the expiration date into an unified format (01-jan-1970).

        Argument:
            - date_to_convert: str
                The date to convert.
        """

        if not date_to_convert:  # pragma: no cover
            # The date to conver is given.

            # We initiate the date we are working with.
            date_to_convert = self.expiration_date

        # We map the different possible regex.
        # The regex index represent a unique number which have to be reported
        # to the self._case_management() method.
        regex_dates = {
            # Date in format: 02-jan-2017
            "1": r"([0-9]{2})-([a-z]{3})-([0-9]{4})",
            # Date in format: 02.01.2017 // Month: jan
            "2": r"([0-9]{2})\.([0-9]{2})\.([0-9]{4})$",
            # Date in format: 02/01/2017 // Month: jan
            "3": r"([0-3][0-9])\/(0[1-9]|1[012])\/([0-9]{4})",
            # Date in format: 2017-01-02 // Month: jan
            "4": r"([0-9]{4})-([0-9]{2})-([0-9]{2})$",
            # Date in format: 2017.01.02 // Month: jan
            "5": r"([0-9]{4})\.([0-9]{2})\.([0-9]{2})$",
            # Date in format: 2017/01/02 // Month: jan
            "6": r"([0-9]{4})\/([0-9]{2})\/([0-9]{2})$",
            # Date in format: 2017.01.02 15:00:00
            "7": r"([0-9]{4})\.([0-9]{2})\.([0-9]{2})\s[0-9]{2}:[0-9]{2}:[0-9]{2}",
            # Date in format: 20170102 15:00:00 // Month: jan
            "8": r"([0-9]{4})([0-9]{2})([0-9]{2})\s[0-9]{2}:[0-9]{2}:[0-9]{2}",
            # Date in format: 2017-01-02 15:00:00 // Month: jan
            "9": r"([0-9]{4})-([0-9]{2})-([0-9]{2})\s[0-9]{2}:[0-9]{2}:[0-9]{2}",
            # Date in format: 02.01.2017 15:00:00 // Month: jan
            "10": r"([0-9]{2})\.([0-9]{2})\.([0-9]{4})\s[0-9]{2}:[0-9]{2}:[0-9]{2}",
            # Date in format: 02-Jan-2017 15:00:00 UTC
            "11": r"([0-9]{2})-([A-Z]{1}[a-z]{2})-([0-9]{4})\s[0-9]{2}:[0-9]{2}:[0-9]{2}\s[A-Z]{1}.*",  # pylint: disable=line-too-long
            # Date in format: 2017/01/02 01:00:00 (+0900) // Month: jan
            "12": r"([0-9]{4})\/([0-9]{2})\/([0-9]{2})\s[0-9]{2}:[0-9]{2}:[0-9]{2}\s\(.*\)",
            # Date in format: 2017/01/02 01:00:00 // Month: jan
            "13": r"([0-9]{4})\/([0-9]{2})\/([0-9]{2})\s[0-9]{2}:[0-9]{2}:[0-9]{2}$",
            # Date in format: Mon Jan 02 15:00:00 GMT 2017
            "14": r"[a-zA-Z]{3}\s([a-zA-Z]{3})\s([0-9]{2})\s[0-9]{2}:[0-9]{2}:[0-9]{2}\s[A-Z]{3}\s([0-9]{4})",  # pylint: disable=line-too-long
            # Date in format: Mon Jan 02 2017
            "15": r"[a-zA-Z]{3}\s([a-zA-Z]{3})\s([0-9]{2})\s([0-9]{4})",
            # Date in format: 2017-01-02T15:00:00 // Month: jan
            "16": r"([0-9]{4})-([0-9]{2})-([0-9]{2})T[0-9]{2}:[0-9]{2}:[0-9]{2}$",
            # Date in format: 2017-01-02T15:00:00Z // Month: jan${'7}
            "17": r"([0-9]{4})-([0-9]{2})-([0-9]{2})T[0-9]{2}:[0-9]{2}:[0-9]{2}[A-Z].*",
            # Date in format: 2017-01-02T15:00:00+0200 // Month: jan
            "18": r"([0-9]{4})-([0-9]{2})-([0-9]{2})T[0-9]{2}:[0-9]{2}:[0-9]{2}[+-][0-9]{4}",
            # Date in format: 2017-01-02T15:00:00+0200.622265+03:00 //
            # Month: jan
            "19": r"([0-9]{4})-([0-9]{2})-([0-9]{2})T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9].*[+-][0-9]{2}:[0-9]{2}",  # pylint: disable=line-too-long
            # Date in format: 2017-01-02T15:00:00+0200.622265 // Month: jan
            "20": r"([0-9]{4})-([0-9]{2})-([0-9]{2})T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}$",
            # Date in format: 2017-01-02T23:59:59.0Z // Month: jan
            "21": r"([0-9]{4})-([0-9]{2})-([0-9]{2})T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9].*[A-Z]",
            # Date in format: 02-01-2017 // Month: jan
            "22": r"([0-9]{2})-([0-9]{2})-([0-9]{4})",
            # Date in format: 2017. 01. 02. // Month: jan
            "23": r"([0-9]{4})\.\s([0-9]{2})\.\s([0-9]{2})\.",
            # Date in format: 2017-01-02T00:00:00+13:00 // Month: jan
            "24": r"([0-9]{4})-([0-9]{2})-([0-9]{2})T[0-9]{2}:[0-9]{2}:[0-9]{2}[+-][0-9]{2}:[0-9]{2}",  # pylint: disable=line-too-long
            # Date in format: 20170102 // Month: jan
            "25": r"(?=[0-9]{8})(?=([0-9]{4})([0-9]{2})([0-9]{2}))",
            # Date in format: 02-Jan-2017
            "26": r"([0-9]{2})-([A-Z]{1}[a-z]{2})-([0-9]{4})$",
            # Date in format: 02.1.2017 // Month: jan
            "27": r"([0-9]{2})\.([0-9]{1})\.([0-9]{4})",
            # Date in format: 02 Jan 2017
            "28": r"([0-9]{1,2})\s([A-Z]{1}[a-z]{2})\s([0-9]{4})",
            # Date in format: 02-January-2017
            "29": r"([0-9]{2})-([A-Z]{1}[a-z]*)-([0-9]{4})",
            # Date in format: 2017-Jan-02.
            "30": r"([0-9]{4})-([A-Z]{1}[a-z]{2})-([0-9]{2})\.",
            # Date in format: Mon Jan 02 15:00:00 2017
            "31": r"[a-zA-Z]{3}\s([a-zA-Z]{3})\s([0-9]{1,2})\s[0-9]{2}:[0-9]{2}:[0-9]{2}\s([0-9]{4})",  # pylint: disable=line-too-long
            # Date in format: Mon Jan 2017 15:00:00
            "32": r"()[a-zA-Z]{3}\s([a-zA-Z]{3})\s([0-9]{4})\s[0-9]{2}:[0-9]{2}:[0-9]{2}",
            # Date in format: January 02 2017-Jan-02
            "33": r"([A-Z]{1}[a-z]*)\s([0-9]{1,2})\s([0-9]{4})",
            # Date in format: 2.1.2017 // Month: jan
            "34": r"([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{4})",
            # Date in format: 20170102000000 // Month: jan
            "35": r"([0-9]{4})([0-9]{2})([0-9]{2})[0-9]+",
            # Date in format: 01/02/2017 // Month: jan
            "36": r"(0[1-9]|1[012])\/([0-3][0-9])\/([0-9]{4})",
            # Date in format: January  2 2017
            "37": r"([A-Z]{1}[a-z].*)\s\s([0-9]{1,2})\s([0-9]{4})",
            # Date in format: 2nd January 2017
            "38": r"([0-9]{1,})[a-z]{1,}\s([A-Z].*)\s(2[0-9]{3})",
        }

        for regx in regex_dates:
            # We loop through our map.

            # We try to get the matched groups if the date to convert match the currently
            # read regex.
            matched_result = Regex(
                date_to_convert, regex_dates[regx], return_data=True, rematch=True
            ).match()

            if matched_result:
                # The matched result is not None or an empty list.

                # We get the date.
                date = self._cases_management(regx, matched_result)

                if date:
                    # The date is given.

                    # We return the formated date.
                    return "-".join(date)

        # We return an empty string as we were not eable to match the date format.
        return ""

    def _extract(self):  # pragma: no cover
        """
        Extract the expiration date from the whois record.
        """

        # We get the whois record.
        self.whois_record = Lookup().whois(PyFunceble.CONFIGURATION["referer"])

        # We list the list of regex which will help us get an unformated expiration date.
        to_match = [
            r"expire:(.*)",
            r"expire on:(.*)",
            r"Expiry Date:(.*)",
            r"free-date(.*)",
            r"expires:(.*)",
            r"Expiration date:(.*)",
            r"Expiry date:(.*)",
            r"Expire Date:(.*)",
            r"renewal date:(.*)",
            r"Expires:(.*)",
            r"validity:(.*)",
            r"Expiration Date             :(.*)",
            r"Expiry :(.*)",
            r"expires at:(.*)",
            r"domain_datebilleduntil:(.*)",
            r"Data de expiração \/ Expiration Date \(dd\/mm\/yyyy\):(.*)",
            r"Fecha de expiración \(Expiration date\):(.*)",
            r"\[Expires on\](.*)",
            r"Record expires on(.*)(\(YYYY-MM-DD\))",
            r"status:      OK-UNTIL(.*)",
            r"renewal:(.*)",
            r"expires............:(.*)",
            r"expire-date:(.*)",
            r"Exp date:(.*)",
            r"Valid-date(.*)",
            r"Expires On:(.*)",
            r"Fecha de vencimiento:(.*)",
            r"Expiration:.........(.*)",
            r"Fecha de Vencimiento:(.*)",
            r"Registry Expiry Date:(.*)",
            r"Expires on..............:(.*)",
            r"Expiration Time:(.*)",
            r"Expiration Date:(.*)",
            r"Expired:(.*)",
            r"Date d'expiration:(.*)",
        ]

        if self.whois_record:
            # The whois record is not empty.

            for string in to_match:
                # We loop through the list of regex.

                # We try tro extract the expiration date from the WHOIS record.
                expiration_date = Regex(
                    self.whois_record, string, return_data=True, rematch=True, group=0
                ).match()

                if expiration_date:
                    # The expiration date could be extracted.

                    # We get the extracted expiration date.
                    self.expiration_date = expiration_date[0].strip()

                    # We initate a regex which will help us know if a number
                    # is present into the extracted expiration date.
                    regex_rumbers = r"[0-9]"

                    if Regex(
                        self.expiration_date, regex_rumbers, return_data=False
                    ).match():
                        # The extracted expiration date has a number.

                        # We format the extracted expiration date.
                        self.expiration_date = self._format()

                        if (
                            self.expiration_date
                            and not Regex(
                                self.expiration_date,
                                r"[0-9]{2}\-[a-z]{3}\-2[0-9]{3}",
                                return_data=False,
                            ).match()
                        ):
                            # The formated expiration date does not match our unified format.

                            # We log the problem.
                            self.log()

                            # We log the whois record.
                            self._whois_log()

                        # We generate the files and print the status.
                        # It's an active element!
                        Generate(
                            PyFunceble.STATUS["official"]["up"],
                            "WHOIS",
                            self.expiration_date,
                        ).status_file()

                        # We log the whois record.
                        self._whois_log()

                        # We handle und return the official up status.
                        return PyFunceble.STATUS["official"]["up"]

                    # The extracted expiration date does not have a number.

                    # We log the whois record.
                    self._whois_log()

                    # We handle and return and h the official down status.
                    return Status(PyFunceble.STATUS["official"]["down"]).handle()

        # The whois record is not empty.

        # We handle and return the official down status.
        return Status(PyFunceble.STATUS["official"]["down"]).handle()

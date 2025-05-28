import unittest
from atlas.stacktrace.parser import parse_stacktrace

class TestStacktraceParser(unittest.TestCase):
    def test_simple_trace(self):
        trace = """
        org.springframework.security.authentication.AuthenticationServiceException: Error during parse token
            at com.primerevenue.tradingengine.api.authentication.JwtProperties.decode(JwtProperties.java:65)
            at org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationProvider.getJwt(JwtAuthenticationProvider.java:99)
            at org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationProvider.authenticate(JwtAuthenticationProvider.java:88)
        """

        expected = [
            {
                "class": "com.primerevenue.tradingengine.api.authentication.JwtProperties",
                "method": "decode",
                "file": "JwtProperties.java",
                "line": 65,
                "is_user_code": True
            },
            {
                "class": "org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationProvider",
                "method": "getJwt",
                "file": "JwtAuthenticationProvider.java",
                "line": 99,
                "is_user_code": False
            },
            {
                "class": "org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationProvider",
                "method": "authenticate",
                "file": "JwtAuthenticationProvider.java",
                "line": 88,
                "is_user_code": False
            }
        ]

        result = parse_stacktrace(trace)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()

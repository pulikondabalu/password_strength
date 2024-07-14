import streamlit as st

class Stat:
    def __init__(self, score: tuple, text: str, *lines: str, color="white", symbol=None): 
        self.score = score
        self.symbol = '>' if symbol is None else symbol
        self.color = color
        self.text = text
        self.lines = lines
    
    def with_info(self, *lines: str):
        if lines: self.lines = self.lines + lines
        return self

class BoolStat(Stat):
    def __init__(self, value: bool):
        super().__init__((1 if value else 0, 1), 'Yes' if value else 'No', color='white' if value else 'white')
        self.symbol = '✔' if value else '✖'

class PasswordStrengthChecker:
    def __init__(self) -> None:
        pass
    
    def _check(self, password: str) -> dict[str, Stat]:
        res = {}

        upper = 0
        lower = 0
        digits = 0
        symbols = 0
        for char in password:
            if char.islower():
                lower += 1
            elif char.isupper():
                upper += 1
            elif char.isdigit():
                digits += 1
            else:
                symbols += 1
        
        _length = len(password)
        mark = ((14 if _length > 14 else _length) / 14) * 3, 3
        if _length >= 14:
            lengthStat = Stat(mark, "Excellent", "Secure against brute force attacks", color="green")
        elif _length >= 11:
            lengthStat = Stat(mark, "Good", "Secure against brute force attacks", color="green")
        elif _length >= 8:
            lengthStat = Stat(mark, "Short", "Possibly crackable by brute force attacks", color="yellow")
        else:
            lengthStat = Stat(mark, "Too short", "Crackable via brute force attacks", "A length of at least 8 is recommended", color="red")

        with open("10k-most-common.txt", 'r') as f:
            found = password + "\n" in f.readlines()
            res[f"{'A' if found else 'Not a'} common password"] = Stat(
                (-5 if found else 0, 0),
                "COMMON" if found else "Uncommon",
                f"{'CRACKABLE. Found' if found else 'Not found'} in 10,000 most common passwords",
                color="red" if found else "white",
                symbol="✖" if found else ">"
            )
        
        res[f"Length ({len(password)})"] = lengthStat
        res[f"Include: uppercase letters ({upper})"] = BoolStat(upper > 0)
        res[f"Include: lowercase letters ({lower})"] = BoolStat(lower > 0) \
            .with_info(f"{'✔ Has' if upper > 0 and lower > 0 else '✖ Does not have'} mix of upper and lower case.")
        res[f"Include: symbols ({symbols})"] = BoolStat(symbols > 0)
        res[f"Include: numbers ({digits})"] = BoolStat(digits > 0)

        return res
    
    def check(self, password):
        res = self._check(password)
        result_str = ""

        result_str += f"Password: {'*' * len(password)}\n"
        
        total_score = 0
        score = 0
        for key, stat in res.items():
            key: str; stat: Stat

            color = stat.color
            result_str += f"{stat.symbol} <span style='color:{color}'>{stat.text}</span> - {key}\n"

            total_score += stat.score[1]
            score += stat.score[0]
            if stat.lines:
                for line in stat.lines:
                    result_str += f"{' ' * (3 + 9 + 2)}{line}\n"
        
        # Scoring
        score = 0 if score < 0 else score
        frac = score / total_score
        if frac >= .8:
            color = 'brightgreen'
        elif frac >= .6:
            color = "green"
        elif frac >= .5:
            color = 'yellow'
        else:
            color = "red"

        result_str += f"\nPassword Strength: <span style='color:{color}'>{str(round(frac * 100, 2))}%</span>\n"

        bar_frac = int(frac * 44)
        bar = f"<span style='color:{color}'>" + '━' * bar_frac + "</span>" + f"<span style='color:gray'>" + '━' * (44 - bar_frac) + "</span>"

        result_str += bar

        return result_str

# Streamlit UI
checker = PasswordStrengthChecker()
st.title('Password Strength Checker')
password = st.text_input('Enter your password', type='password')

if password:
    result = checker.check(password)
    st.markdown(result, unsafe_allow_html=True)

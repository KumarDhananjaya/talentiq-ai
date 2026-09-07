import re
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader

from app.schemas.resume import (
    EducationItem,
    ExperienceItem,
    ParsedResume,
)


SKILL_DICTIONARY = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C++",
    "C",
    "React",
    "Next.js",
    "Node.js",
    "Express.js",
    "FastAPI",
    "Django",
    "Flask",
    "Machine Learning",
    "Deep Learning",
    "TensorFlow",
    "PyTorch",
    "scikit-learn",
    "SQL",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "Git",
    "GitHub",
    "GitHub Actions",
    "Pandas",
    "NumPy",
    "XGBoost",
    "LangChain",
    "LLM",
    "Large Language Models",
    "Generative AI",
    "OpenAI",
]


def normalize_pdf_text(text: str) -> str:
    """
    Fix garbled text caused by PDF font subset encoding issues.

    Some PDFs use a private-use font subset where digits 0-9
    are remapped to punctuation/symbol glyphs.

    Observed mapping:
        ! -> 2
        " -> 0
        # -> 3
        $ -> 4
        % -> 5
        & -> 2
        ' -> 4
    """

    glyph_map = str.maketrans(
        {
            "!": "2",
            '"': "0",
            "#": "3",
            "$": "4",
            "%": "5",
            "&": "2",
            "'": "4",
            "\u2019": "4",
        }
    )

    glyph_chars = set('!"#$%&\'\u2019')

    glyph_pattern = re.compile(
        r'[!"#$%&\'\u2019]'
    )

    lines = []

    for line in text.splitlines():
        tokens = line.split()
        fixed_tokens = []

        for token in tokens:

            if not glyph_pattern.search(token):
                fixed_tokens.append(token)
                continue

            alpha_chars = sum(
                1 for char in token if char.isalpha()
            )

            glyph_count = sum(
                1
                for char in token
                if char in glyph_chars
            )

            digit_count = sum(
                1
                for char in token
                if char.isdigit()
            )

            # Always normalize email tokens.
            if "@" in token:
                fixed_tokens.append(
                    token.translate(glyph_map)
                )

            # Pure glyph/digit tokens.
            elif alpha_chars == 0:
                fixed_tokens.append(
                    token.translate(glyph_map)
                )

            # Glyphs outnumber or equal alphabetic characters.
            elif glyph_count >= alpha_chars:
                fixed_tokens.append(
                    token.translate(glyph_map)
                )

            # Digits + glyphs outnumber alphabetic characters.
            elif (
                glyph_count + digit_count
            ) > alpha_chars:
                fixed_tokens.append(
                    token.translate(glyph_map)
                )

            else:
                fixed_tokens.append(token)

        lines.append(" ".join(fixed_tokens))

    return "\n".join(lines)


def extract_text_from_pdf(
    file_path: str,
) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Resume file not found: {file_path}"
        )

    raw_text = ""

    # Try PyMuPDF first because it generally preserves
    # layout better.
    try:
        import pymupdf  # type: ignore

        doc = pymupdf.open(str(path))

        pages = [
            page.get_text()
            for page in doc
        ]

        raw_text = "\n".join(pages).strip()

    except ImportError:
        pass

    # Fall back to pypdf.
    if not raw_text:
        reader = PdfReader(path)

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        raw_text = "\n".join(pages).strip()

    return normalize_pdf_text(raw_text)


def extract_email(
    text: str,
) -> str | None:
    """
    Extract an email address from potentially garbled PDF text.
    """

    if "@" not in text:
        return None

    glyph_map = str.maketrans(
        {
            "!": "2",
            '"': "0",
            "#": "3",
            "$": "4",
            "%": "5",
            "&": "2",
            "'": "4",
            "\u2019": "4",
        }
    )

    strict_pattern = re.compile(
        r"[A-Za-z0-9._%+\-]+"
        r"@"
        r"[A-Za-z0-9.-]+"
        r"\."
        r"[A-Za-z]{2,}"
    )

    broad_pattern = re.compile(
        r'[A-Za-z0-9._%+\-!"#$&\'\u2019]+'
        r"@"
        r"[A-Za-z0-9.-]+"
        r"\."
        r"[A-Za-z]{2,}"
    )

    # Fast path for clean emails.
    match = strict_pattern.search(text)

    if match:
        return match.group(0)

    # Handle spaces inserted by PDF extraction.
    words = text.split()

    for index, word in enumerate(words):

        if "@" not in word:
            continue

        start = max(0, index - 2)
        end = min(len(words), index + 3)

        context = "".join(
            words[start:end]
        )

        match = broad_pattern.search(context)

        if match:
            email = match.group(0)

            local, _, domain = email.partition("@")

            local = local.translate(
                glyph_map
            )

            return f"{local}@{domain}"

    return None


def extract_phone(
    text: str,
) -> str | None:

    pattern = (
        r"(?:\+?\d{1,3}[\s.-]?)?"
        r"(?:\(?\d{2,4}\)?[\s.-]?)?"
        r"\d{3,4}[\s.-]?"
        r"\d{3,4}[\s.-]?"
        r"\d{0,4}"
    )

    matches = re.finditer(
        pattern,
        text,
    )

    for match in matches:

        phone = match.group(0).strip()

        digits = re.sub(
            r"\D",
            "",
            phone,
        )

        if 9 <= len(digits) <= 15:
            return phone

    return None


def extract_skills(
    text: str,
) -> list[str]:

    detected_skills = []

    for skill in SKILL_DICTIONARY:

        flags = (
            0
            if len(skill) <= 2
            else re.IGNORECASE
        )

        pattern = (
            r"(?<![a-zA-Z0-9+#.-])"
            + re.escape(skill)
            + r"(?![a-zA-Z0-9+#.-])"
        )

        if re.search(
            pattern,
            text,
            flags,
        ):
            detected_skills.append(skill)

    return detected_skills


def extract_full_name(
    text: str,
) -> str | None:

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:10]:

        if "@" in line:
            continue

        if len(line) < 3 or len(line) > 60:
            continue

        if re.search(
            r"\d|http|linkedin|github|portfolio",
            line,
            re.IGNORECASE,
        ):
            continue

        words = line.split()

        if (
            2 <= len(words) <= 4
            and all(
                word[0].isupper()
                for word in words
                if word.isalpha()
            )
        ):
            return re.sub(
                r"[^\w\s-]",
                "",
                line,
            ).strip()

    return None


def extract_location(
    text: str,
) -> str | None:

    pattern = (
        r"(Sydney|Melbourne|Brisbane|Perth|"
        r"Adelaide|Mysuru|Bangalore|Mysore|"
        r"New York|London)"
        r"[\s,]*"
        r"(NSW|VIC|QLD|WA|SA|TAS|ACT|NT|"
        r"Australia|India|USA|UK)?"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE,
    )

    if not match:
        return None

    city = match.group(1).title()

    region = (
        match.group(2).title()
        if match.group(2)
        else ""
    )

    region_upper = region.upper()

    if region_upper in {
        "NSW",
        "VIC",
        "QLD",
        "WA",
        "SA",
        "TAS",
        "ACT",
        "NT",
        "USA",
        "UK",
    }:
        region = region_upper

    return (
        f"{city}, {region}"
        if region
        else city
    )


def extract_experience(
    text: str,
) -> list[ExperienceItem]:

    experiences = []

    months = (
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|"
        r"Sep|Oct|Nov|Dec)[a-zA-Z]*"
    )

    month_year = (
        rf"{months}\s*\d{{4}}"
    )

    numeric_year = r"\d{1,2}/\d{4}"

    just_year = r"(?:19|20)\d{2}"

    garbled_month_year = (
        rf"{months}\s+\S{{2,6}}"
    )

    date_term = (
        rf"(?:{month_year}|"
        rf"{numeric_year}|"
        rf"{just_year}|"
        rf"{garbled_month_year})"
    )

    date_pattern = re.compile(
        rf"({date_term}\s*"
        rf"(?:[-–—|]+|to)\s*"
        rf"(?:Present|Current|Now|{date_term}))",
        re.IGNORECASE,
    )

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for index, line in enumerate(lines):

        match = date_pattern.search(line)

        if not match:
            continue

        duration = match.group(0).strip()

        role_line = (
            line.replace(
                duration,
                "",
            ).strip()
        )

        # If duration is on its own line,
        # inspect surrounding lines.
        if len(role_line) < 5:

            if (
                index > 0
                and len(lines[index - 1]) > 4
            ):
                role_line = lines[index - 1]

            elif (
                index + 1 < len(lines)
                and len(lines[index + 1]) > 4
            ):
                role_line = lines[index + 1]

        role_line = re.sub(
            r"[^a-zA-Z0-9\s,&/|\-]",
            "",
            role_line,
        ).strip()

        if not role_line:
            continue

        if len(role_line) > 100:
            continue

        words_in_role = role_line.split()

        if len(words_in_role) < 2:
            continue

        # Ignore education entries.
        if re.search(
            r"\b("
            r"Bachelor|Master|Doctor|PhD|"
            r"B\.E\.|B\.Tech|M\.Tech|"
            r"University|Institute|College|"
            r"School|CGPA|Expected"
            r")\b",
            role_line,
            re.IGNORECASE,
        ):
            continue

        # Prevent duplicate roles.
        if (
            experiences
            and experiences[-1].role
            == role_line[:80]
        ):
            continue

        experiences.append(
            ExperienceItem(
                role=role_line[:80],
                duration=duration,
            )
        )

    return experiences[:10]


def extract_education(
    text: str,
) -> list[EducationItem]:

    education = []

    degree_patterns = [
        r"(Master(?:'s)? (?:of|in) [A-Za-z &]+)",
        r"(Bachelor(?:'s)? (?:of|in) [A-Za-z &]+)",
        r"(B\.?E\.?(?:\s+in)?\s+[A-Za-z &]+)",
        r"(B\.?Tech(?:\s+in)?\s+[A-Za-z &]+)",
    ]

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for index, line in enumerate(lines):

        for pattern in degree_patterns:

            match = re.search(
                pattern,
                line,
                re.IGNORECASE,
            )

            if not match:
                continue

            degree = match.group(1).strip()

            institution = None

            start_index = max(
                0,
                index - 2,
            )

            end_index = min(
                len(lines),
                index + 3,
            )

            for current_index in range(
                start_index,
                end_index,
            ):

                current_line = lines[
                    current_index
                ]

                if (
                    current_index == index
                    and "-" in line
                ):
                    parts = line.split("-")

                    for part in parts:

                        if re.search(
                            r"(University|Institute|"
                            r"College|School)",
                            part,
                            re.IGNORECASE,
                        ):
                            institution = (
                                part.strip()
                            )

                elif re.search(
                    r"(University|Institute|"
                    r"College|School)",
                    current_line,
                    re.IGNORECASE,
                ):
                    institution = current_line.strip()
                    break

            if institution:
                institution = re.sub(
                    r"[^\w\s,&-]",
                    "",
                    institution,
                ).strip()

            education.append(
                EducationItem(
                    degree=degree,
                    institution=institution,
                )
            )

            break

    return education[:5]


def calculate_experience_years(
    experiences: list[ExperienceItem],
) -> float | None:

    if not experiences:
        return None

    total_years = 0.0

    for experience in experiences:

        years = re.findall(
            r"\b(19\d{2}|20\d{2})\b",
            experience.duration,
        )

        if not years:
            continue

        start_year = int(years[0])

        if re.search(
            r"(present|current|now)",
            experience.duration,
            re.IGNORECASE,
        ):
            end_year = datetime.now().year

        elif len(years) >= 2:
            end_year = int(years[1])

        else:
            end_year = start_year

        difference = (
            end_year - start_year
        )

        if difference == 0:
            total_years += 0.5

        elif difference > 0:
            total_years += difference

    return (
        round(total_years, 1)
        if total_years > 0
        else None
    )


def parse_resume(
    text: str,
) -> ParsedResume:

    experiences = extract_experience(text)

    return ParsedResume(
        full_name=extract_full_name(text),
        email=extract_email(text),
        phone=extract_phone(text),
        location=extract_location(text),
        skills=extract_skills(text),
        experience=experiences,
        education=extract_education(text),
        total_experience_years=(
            calculate_experience_years(
                experiences
            )
        ),
    )
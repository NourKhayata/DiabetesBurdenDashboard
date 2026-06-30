---
title: "Global Diabetes Burden and Treatment Outcomes Dashboard"
subtitle: "User Manual: A Consultant-to-Client Guide"
author: "Prepared by Nour Khayata · MSBA382 Healthcare Analytics Individual Project"
date: "June 2026"
---

# 1. What this dashboard does

This guide walks you through the Global Diabetes Burden and Treatment Outcomes
Dashboard: what it shows, where the numbers come from, and how to pull answers out of
it. Keep it next to you the first few times you open the tool, and put it away once the
workflow starts to feel familiar.

The dashboard pulls the worldwide picture of diabetes onto a single screen. In one place
you can see where the disease hits hardest, how the numbers have shifted since 2000, who
carries the most risk, and how the main treatment options compare.

What sets it apart from an ordinary report is that the charts talk to each other. Click a
country on the map and the trend line, the country rankings, the age and gender
breakdowns, and the headline figures all refocus on that country at the same time. Click
an age group and everything narrows again. You ask a question by clicking, and the whole
page answers at once.

Most people use it to work through questions like these:

- Which countries carry the heaviest diabetes burden, and does the answer change
  depending on which measure you look at?
- How have prevalence, incidence, mortality, and recovery moved between 2000 and 2024?
- Where do the gaps sit across age groups, and between men and women?
- Which treatments give the best recovery for the money?
- How does one country or group compare against the global average?

It is built for people who need those answers quickly, such as health strategists, policy
analysts, and program managers, and it never asks you to write a single line of code.

# 2. Getting started

Behind the scenes the tool runs on Python, with Streamlit handling the web page, pandas
managing the data, and Plotly drawing the charts. You don't need to touch any of that to
use it, but here is how to get it running.

The first time, install the requirements with `pip install -r requirements.txt`. That
brings in Streamlit (version 1.35 or newer), pandas, and Plotly. The Streamlit version
matters: anything older than 1.35 won't register the chart clicks, and the whole tool
leans on those clicks.

After that, start it from the project folder with `streamlit run dashboard_nour.py`. A
browser tab opens on its own. Everything runs locally on your machine, so none of the
data leaves your computer.

You'll land on a login screen first. Type the password and click Login. The password is
`Nourdiabetes2026`. It is a simple gate meant for a course and demo setting, not a full
security system, so treat it as a courtesy lock rather than a vault.

# 3. Where the data comes from

The dashboard sits on top of the Global Health Statistics dataset published on Kaggle
(kaggle.com/datasets/malaiarasugraj/global-health-statistics). It is a public collection
of disease, treatment, and socio-economic figures that spans many countries and years.

Since this project is only about diabetes, a short script (`prepare_data.py`) trims the
original file down to the diabetes rows and saves them as `diabetes_data.csv`. The
dashboard reads that smaller file, which keeps it quick to load, and it holds the data in
memory after the first read so your clicks feel instant from then on.

Here is what the working file contains:

| Property | Value |
|---|---|
| Records (rows) | 50,020 |
| Variables (columns) | 22 |
| Countries | 20 (Argentina, Australia, Brazil, Canada, China, France, Germany, India, Indonesia, Italy, Japan, Mexico, Nigeria, Russia, Saudi Arabia, South Africa, South Korea, Turkey, UK, USA) |
| Years covered | 2000 to 2024 (25 years) |
| Genders | Female, Male, Other |
| Age groups | 0-18, 19-35, 36-60, 61+ |
| Treatment types | Medication, Surgery, Therapy, Vaccination |

One word of caution before you read too much into the figures. This is a public, partly
synthetic dataset built for practice and learning. A few of the treatment labels,
vaccination and surgery for instance, are not really how diabetes is treated in real
life, and the numbers themselves should not be taken as medical fact. Think of the
dashboard as a way to explore patterns and demonstrate the analytics, not as a source of
clinical or policy advice.

# 4. The variables

The table below lists all 22 fields in the dataset: what each one means, the values you
will see, and whether the dashboard puts it to work or simply keeps it on hand. The
fields marked "available" are present in the data and show up in tooltips or the data
table, ready to build on in a later version.

| Variable | Type | Range or values | Role in the dashboard |
|---|---|---|---|
| Country | Text | 20 countries | Filter, plus map and ranking selector |
| Year | Whole number | 2000 to 2024 | Filter (slider) and trend axis |
| Disease Name | Text | "Diabetes" (constant) | Sets the dataset scope |
| Disease Category | Text | 11 categories | Available |
| Prevalence Rate (%) | Decimal | 0.1 to 20.0 | Indicator and KPI |
| Incidence Rate (%) | Decimal | 0.1 to 15.0 | Indicator |
| Mortality Rate (%) | Decimal | 0.1 to 10.0 | Indicator, KPI, scatter bubble size |
| Age Group | Text | 0-18, 19-35, 36-60, 61+ | Filter and age selector |
| Gender | Text | Female, Male, Other | Filter and gender selector |
| Population Affected | Whole number | about 1,000 to 1,000,000 | Available |
| Healthcare Access (%) | Decimal | 50 to 100 | Map and scatter tooltips |
| Doctors per 1000 | Decimal | 0.5 to 5.0 | Available |
| Hospital Beds per 1000 | Decimal | 0.5 to 10.0 | Available |
| Treatment Type | Text | Medication, Surgery, Therapy, Vaccination | Color in the treatment chart |
| Average Treatment Cost (USD) | Whole number | 100 to 50,000 | Scatter horizontal axis |
| Availability of Vaccines/Treatment | Text | Yes or No | Available |
| Recovery Rate (%) | Decimal | 50 to 99 | Indicator, KPI, scatter vertical axis |
| DALYs | Whole number | 1 to 5,000 | Available (Disability-Adjusted Life Years) |
| Improvement in 5 Years (%) | Decimal | 0 to 10 | Available |
| Per Capita Income (USD) | Whole number | 500 to 99,999 | Available |
| Education Index | Decimal | 0.4 to 0.9 | Available |
| Urbanization Rate (%) | Decimal | 20 to 90 | Available |

When this manual mentions the "main indicator," it means one of four measures you can
switch between: prevalence, incidence, mortality, and recovery. Whichever you pick
recolors the map and redraws the trend, ranking, age, and gender charts around it.

# 5. A tour of the screen

The dashboard is one long page. Working down from the top:

**The sidebar** on the left is where you set the scene. You choose which countries to
include (all of them to start), drag a slider to pick the year range, tick the genders
and age groups you care about, and pick the main indicator from a dropdown. If you ever
filter so far that nothing is left, the page tells you plainly instead of going blank.

**The selection banner and Reset button** sit just under the title. The colored banner
always reminds you what is currently in focus: the country, age, and gender you have
clicked into, and the indicator driving the charts. When you want a clean slate, the
Reset selection button clears every chart click in one tap.

**The KPI strip** is the row of five cards beneath that: total records, number of
countries, and the average prevalence, mortality, and recovery for whatever you are
looking at. They recompute the instant you change a filter or click a chart.

**Row one** pairs a world map with a trend line. The map shades each country by your
chosen indicator on a blue scale, where darker means higher, and hovering shows the
prevalence, mortality, recovery, and healthcare access for that country. Click a country
to focus the entire page on it. The trend line on the right then shows how that indicator
has moved year by year from 2000 to 2024.

**Row two** pairs a country ranking with a treatment chart. The ranking bar lists
countries from highest to lowest on your chosen indicator, with the one you have selected
highlighted in dark blue and the rest faded back. Clicking a bar filters the page, and
because the map and the ranking both control "country," they work as a pair. The chart on
the right plots each treatment type by its average cost (across the bottom) against its
recovery rate (up the side), with bubble size showing mortality and color marking the
treatment. It is the quickest way to spot which treatments give strong recovery without a
heavy price tag.

**Row three** holds two more bar charts, one breaking the indicator down by age group
(ordered youngest to oldest) and one by gender. Click any bar to fold that age group or
gender into your selection.

Below the charts you'll find two short notes, one explaining how the views are linked and
one repeating the data caution so results are read in the right spirit. Last comes an
expandable panel that shows the exact table behind your current view, with a Download
Selected Data button that saves it as a CSV. The footer simply credits the author and the
course.

# 6. How the linking works

This is the part that makes the tool feel like one connected story rather than a wall of
separate charts. Two things combine to control what you see. The sidebar sets the broad
context, the countries, years, genders, ages, and indicator in play. Your chart clicks
then layer a finer selection on top.

The charts fall into two camps. Some are there for you to click: the map, the country
ranking, the age bar, and the gender bar. The rest react to whatever you have chosen:
the trend line, the treatment chart, and the KPI cards. Because the map and the ranking
both point at the same "country" idea, a click on either one counts as the same choice.

There is one small touch worth knowing. A chart you click never filters itself out of
view. Pick one country on the ranking bar and the bar still shows every country, so you
can keep comparing and switching, while the trend, the treatment chart, and the KPIs
narrow to your pick. When you want to start over, Reset selection clears it all at once.

# 7. Ways people use it

A common first move is to compare two countries. Set the indicator to prevalence, click
one country on the map and read its trend, hit Reset, click a second country, and put the
two stories side by side in your head.

Another is hunting for the best-value treatment. On the treatment chart, the sweet spot
sits high and to the left: strong recovery, lower cost, and a small bubble for lower
mortality.

You can also profile a specific group. Click the 61+ age bar and the Female gender bar
together, and the KPIs and trend now describe exactly that population, while the map
shows where their burden is concentrated.

And when you have narrowed things down to the slice you care about, open the data panel
and download it, so you can carry the exact figures into a report or a slide deck.

# 8. Reading the results responsibly

A few habits will keep your conclusions sound. Glance at the banner first so you know
which indicator is driving the charts, since everything redraws around it. Remember that
the KPIs and most charts show averages across your current selection, which is why they
move as you filter. Keep the data caution from Section 3 in mind: the figures come from a
public practice dataset and are not a basis for clinical or investment decisions. And note
the fixed scope, 20 countries and the years 2000 to 2024, with no live or outside data
flowing in.

# 9. If something goes wrong

| What you see | What to do |
|---|---|
| Charts don't react when you click | Your Streamlit is older than 1.35. Run `pip install -r requirements.txt` to update it. |
| "No data available for the selected filters" | Your filters are too tight. Widen the country, year, gender, or age choices in the sidebar. |
| A selection feels stuck | Click Reset selection to clear every chart click. |
| Login keeps failing | Re-type the password exactly: `Nourdiabetes2026` (it is case-sensitive). |
| The app won't start | Make sure `diabetes_data.csv` sits in the same folder as `dashboard_nour.py`, and that the requirements are installed. |

---

*Prepared by Nour Khayata for the MSBA382 Healthcare Analytics Individual Project.
Dashboard topic: Global Diabetes Burden and Treatment Outcomes.*

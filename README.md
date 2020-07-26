# Cleric
An assistant for the purpose of ticket triage, escalation to crisis intervention, and crisis tracking.

# How to Use
Cleric currently has the following commands using `c;` as a prefix (`c;ping` for example):

- `ping` - pong
- `crisis` - escalate ticket to a crisis ticket. pings @Crisis Team. Auto posts a link to the PHQ9 questionnaire. 
- `qpr` - use the following format `c;qpr @user qpr_score time_before_follow_up plan_for_progress`. For example you could try `c;qpr @thumb 7 7d practice deep breathing`. This command saves a record of DQPR taking place and provides a date for follow up.
- `screening` - use with `c;screening id`. Cleric will post a record of the specific screening.
- `history` - `c;history @user` will post a record of past screenings for user if any exist.
- `discharge` - `c;discharge id` removes screening from database.

# Other Information

- Most commands will be accessible to both @Moderators and @Helpers
- Cleric is initially activated for triage when ticket tool posts it's initial ticket message. This activation requires that ticket tool pings @Helpers, meaning that it will only be used in the help category.
- Cleric posts a triage message that allows a user to decide what kind of help they need. This will let @Helpers that don't feel comfortable with certain types of support decide if they should let someone else handle the ticket.




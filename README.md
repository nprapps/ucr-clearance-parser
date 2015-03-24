# UCR Clearance Parser Notes

Cross walk file converted with R

Handy query: 

```
select a.agency, a.state,  c.violent_count, a.agentype, c.violent_cleared, c.violent_cleared_pct from clearance_rates as c join agencies as a on a.ori7 = c.lea_code;
```

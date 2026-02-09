-- PostgreSQL
-- 1) создаём временную таблицу с вычисляемыми полями
--    real_income = (amount + percent_amount) * (1 - 4.5%)
--    real_annual_yield = ((real_income - amount) / amount) * (365 / period_days)

DROP TABLE if EXISTS tmp_requests_yield;
CREATE TEMP TABLE tmp_requests_yield AS
SELECT
  r.id, r.amount, r.period_days, r.interest_rate ,

  -- 1) реальный доход (итоговая сумма на руках с учётом -4.5%)
  ROUND((r.amount + r.percent_amount) * 0.955, 2) AS real_income,

  -- 2) реальная годовая доходность (простая, линейная)
ROUND(
  (
    (((r.amount + r.percent_amount) * 0.955) - r.amount)
    / NULLIF(r.amount, 0)
  ) * (365.0 / NULLIF(r.period_days, 0)) * 100
, 2) AS real_year_interest_rate,

  -- 4) "сортировка внутри групп" через ранг в группе
  ROW_NUMBER() OVER (
    PARTITION BY r.period_days
    ORDER BY
      (
        ((((r.amount + r.percent_amount) * 0.955) - r.amount) / NULLIF(r.amount, 0))
        * (365.0 / NULLIF(r.period_days, 0))
      ) DESC
  ) AS rn_in_period

FROM requests r;

-- 3) группировка по period_days + 4) сортировка внутри групп по реальной годовой доходности
SELECT *
FROM tmp_requests_yield
ORDER BY period_days, real_year_interest_rate DESC;

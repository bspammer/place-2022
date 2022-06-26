-- brady smirk
select distinct userId from place
where x >= 73 and x <=73
and y >= 784 and y <=784
and color = '#FFA800'

-- bees
intersect select distinct userId from place
where x >= 48 and x <= 58
and y >= 798 and y <= 830

-- glorious nail and gear forever
intersect select distinct userId from place
where x >= 58 and x <= 70
and y >= 809 and y <= 825
and color = '#898D90'
and userId = 'YOzyKcsX+88ez536'

;

-- result: YOzyKcsX+88ez536

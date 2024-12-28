/*global Calendar, findPosX, findPosY, get_format, gettext, gettext_noop, interpolate, ngettext, quickElement*/
'use strict';
{
    const DateTimeShortcuts = {
        calendars: [],
        calendarInputs: [],
        dismissCalendarFunc: [],
        calendarDivName1: 'calendarbox', // имя <div> календаря, который переключается
        calendarDivName2: 'calendarin',  // имя <div>, который содержит календарь
        init: function() {
            console.log('DateTimeShortcuts initialized');
            for (const inp of document.getElementsByTagName('input')) {
                if (inp.type === 'text' && inp.classList.contains('vDateField')) {
                    console.log('Found vDateField input:', inp);
                    inp.setAttribute('autocomplete', 'off'); // Запрет браузерных подсказок
                    DateTimeShortcuts.addCalendar(inp);
                }
            }
        },
        addCalendar: function(inp) {
            const num = DateTimeShortcuts.calendars.length;
            DateTimeShortcuts.calendarInputs[num] = inp;
            DateTimeShortcuts.dismissCalendarFunc[num] = function() { DateTimeShortcuts.dismissCalendar(num); return true; };

            const cal_box = document.createElement('div');
            cal_box.style.display = 'none';
            cal_box.style.position = 'absolute';
            cal_box.className = 'calendarbox module';
            cal_box.id = DateTimeShortcuts.calendarDivName1 + num;
            document.body.appendChild(cal_box);
            cal_box.addEventListener('click', function(e) { e.stopPropagation(); });

            const cal_main = document.createElement('div');
            cal_main.id = DateTimeShortcuts.calendarDivName2 + num;
            cal_main.className = 'calendar';
            cal_box.appendChild(cal_main);

            // Добавление элементов управления месяцами
            const cal_nav = document.createElement('div');
            cal_nav.className = 'cal-nav';
            cal_box.appendChild(cal_nav);

            const prev_link = document.createElement('a');
            prev_link.href = '#';
            prev_link.className = 'cal-prev';
            prev_link.innerHTML = '&laquo;'; // Символ стрелки влево
            prev_link.addEventListener('click', function(e) {
                e.preventDefault();
                DateTimeShortcuts.calendars[num].drawPreviousMonth();
            });
            cal_nav.appendChild(prev_link);

            const month_label = document.createElement('span');
            month_label.className = 'cal-month-label';
            cal_nav.appendChild(month_label);

            const next_link = document.createElement('a');
            next_link.href = '#';
            next_link.className = 'cal-next';
            next_link.innerHTML = '&raquo;'; // Символ стрелки вправо
            next_link.addEventListener('click', function(e) {
                e.preventDefault();
                DateTimeShortcuts.calendars[num].drawNextMonth();
            });
            cal_nav.appendChild(next_link);

            console.log('Initializing Calendar for input:', inp);
            DateTimeShortcuts.calendars[num] = new Calendar(cal_main.id, DateTimeShortcuts.handleCalendarCallback(num));
            DateTimeShortcuts.calendars[num].drawCurrent();

            inp.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                DateTimeShortcuts.openCalendar(num);
            });

            document.addEventListener('keyup', function(event) {
                if (event.key === 'Escape' || event.keyCode === 27) { // для кроссбраузерной совместимости
                    DateTimeShortcuts.dismissCalendar(num);
                    event.preventDefault();
                }
            });
        },
        openCalendar: function(num) {
            const cal_box = document.getElementById(DateTimeShortcuts.calendarDivName1 + num);
            const inp = DateTimeShortcuts.calendarInputs[num];

            if (inp.value) {
                const format = get_format('DATE_INPUT_FORMATS')[0];
                const selected = inp.value.strptime(format);
                const year = selected.getUTCFullYear();
                const month = selected.getUTCMonth() + 1;
                const re = /\d{4}/;
                if (re.test(year.toString()) && month >= 1 && month <= 12) {
                    DateTimeShortcuts.calendars[num].drawDate(month, year, selected);
                }
            }

            if (window.getComputedStyle(document.body).direction !== 'rtl') {
                cal_box.style.left = findPosX(inp) + 17 + 'px';
            } else {
                cal_box.style.left = findPosX(inp) - 180 + 'px';
            }
            cal_box.style.top = Math.max(0, findPosY(inp) - 75) + 'px';

            cal_box.style.display = 'block';
            setTimeout(() => { // Добавление задержки для предотвращения немедленного закрытия календаря
                document.addEventListener('click', DateTimeShortcuts.dismissCalendarFunc[num]);
            }, 10);
        },
        dismissCalendar: function(num) {
            const cal_box = document.getElementById(DateTimeShortcuts.calendarDivName1 + num);
            if (cal_box) {
                cal_box.style.display = 'none';
                document.removeEventListener('click', DateTimeShortcuts.dismissCalendarFunc[num]);
            }
        },
        handleCalendarCallback: function(num) {
            const format = get_format('DATE_INPUT_FORMATS')[0];
            return function(y, m, d) {
                DateTimeShortcuts.calendarInputs[num].value = new Date(y, m - 1, d).strftime(format);
                DateTimeShortcuts.calendarInputs[num].focus();
                document.getElementById(DateTimeShortcuts.calendarDivName1 + num).style.display = 'none';
            };
        }
    };

    window.addEventListener('load', DateTimeShortcuts.init);
    window.DateTimeShortcuts = DateTimeShortcuts;
}
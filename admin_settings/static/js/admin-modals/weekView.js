export function renderWeekView(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.warn(`Container with id "${containerId}" not found`);
        return;
    }

    // Если данные не пришли или нет необходимых полей
    if (!data || !data.days|| !data.tables || !data.week_schedule) {
        container.innerHTML = '<div class="p-4 text-center text-gray-500">Нет данных для отображения</div>';
        return;
    }

    // Проверяем, является ли день рабочим
    const today = new Date().toISOString().split('T')[0];
    const isWorkingDay = data.days.some(day => {
        const dayDate = day.split('T')[0];
        return dayDate === today && data.week_schedule[data.tables[0].id]?.[day]?.is_working_day;
    });

    if (!isWorkingDay) {
        container.innerHTML = `
            <div class="text-center py-8 bg-gray-100 rounded-lg">
                <h3 class="text-lg font-medium text-gray-700">Сегодня выходной день</h3>
                <p class="text-gray-500 mt-2">Бронирование столов недоступно</p>
            </div>
        `;
        return;
    }

    // Генерация HTML (используется шаблон из week_view.html)
    container.innerHTML = `
        <div class="min-w-[800px]">
            <div class="grid grid-cols-8 gap-1 mb-2">
                <div class="p-2 font-medium"></div>
                ${data.days.map(day => {
                    const dayDate = new Date(day);
                    return `
                        <div class="p-2 text-center font-medium">
                            <div>${dayDate.toLocaleDateString('ru-RU', { weekday: 'short' })}</div>
                            <div>${dayDate.getDate()}</div>
                        </div>
                    `;
                }).join('')}
            </div>
            
            <div class="grid grid-cols-8 gap-1">
                <div class="flex flex-col">
                    ${data.tables.map(table => `
                        <div class="p-2 border-b flex items-center justify-between">
                            <span>Стол #${table.number}</span>
                            <span class="text-xs text-gray-500">${table.table_type}</span>
                        </div>
                    `).join('')}
                </div>
                
                ${data.days.map(day => `
                    <div class="flex flex-col">
                        ${data.tables.map(table => {
                            const availability = data.week_schedule[table.number]?.[day] || {};
                            return `
                                <div class="p-2 border-b text-center 
                                    ${!availability.is_working_day ? 'bg-gray-100 text-gray-500' :
                                    availability.total_slots === 0 ? 'bg-gray-200 text-gray-600' :
                                    availability.booked_slots === availability.total_slots ? 'bg-red-100 text-red-800' :
                                    'bg-green-50 text-green-800'}">
                                    ${availability.is_working_day ? 
                                        `${availability.booked_slots}/${availability.total_slots}` : 
                                        'Выходной'}
                                </div>
                            `;
                        }).join('')}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}
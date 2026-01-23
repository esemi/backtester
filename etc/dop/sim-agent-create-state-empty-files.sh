#!/bin/bash

# Цикл от 1 до 50
for i in {1..50}; do
    # Формируем путь к директории
    dir="/home/trader$i"
    
    # Проверяем, существует ли директория
    if [ -d "$dir" ]; then
        # Создаём пустой файл state.pickle в директории
        touch "$dir/state.pickle"
        
        # Устанавливаем владельца и группу
        chown "trader$i:admin-agent" "$dir/state.pickle"
		
		# Устанавливаем права 0666 (rw-rw-rw-)
        chmod 0666 "$dir/state.pickle"
        
        echo "Файл создан и права установлены для $dir/state.pickle"
    else
        echo "Директория $dir не существует, пропускаем"
    fi
done

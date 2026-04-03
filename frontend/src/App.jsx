import { useState, useEffect, useCallback } from 'react';
import { getItems, createItem, toggleItem } from './api';

const DEFAULT_USER_ID = Number(import.meta.env.VITE_DEFAULT_USER_ID) || 1;

const CATEGORY_COLORS = {
  'Овощи': 'bg-green-100 text-green-800',
  'Фрукты': 'bg-yellow-100 text-yellow-800',
  'Молочка': 'bg-blue-100 text-blue-800',
  'Мясо': 'bg-red-100 text-red-800',
  'Бакалея': 'bg-amber-100 text-amber-800',
  'Другое': 'bg-gray-100 text-gray-800',
};

function App() {
  const [items, setItems] = useState([]);
  const [newItemName, setNewItemName] = useState('');
  const [newItemCategory, setNewItemCategory] = useState('Другое');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchItems = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const { data } = await getItems(DEFAULT_USER_ID);
      setItems(data);
    } catch {
      setError('Не удалось загрузить список покупок');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleAddItem = async (e) => {
    e.preventDefault();
    const name = newItemName.trim();
    if (!name) return;

    try {
      setError(null);
      const { data } = await createItem({
        name,
        category: newItemCategory,
        user_id: DEFAULT_USER_ID,
      });
      setItems((prev) => [...prev, data]);
      setNewItemName('');
      setNewItemCategory('Другое');
    } catch {
      setError('Не удалось добавить товар');
    }
  };

  const handleToggle = async (item) => {
    try {
      setError(null);
      const { data } = await toggleItem(item.id);
      setItems((prev) =>
        prev.map((it) => (it.id === item.id ? data : it))
      );
    } catch {
      setError('Не удалось обновить статус');
    }
  };

  const boughtCount = items.filter((i) => i.is_bought).length;

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-emerald-600 text-white shadow-lg">
        <div className="max-w-2xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            🛒 Мои покупки
          </h1>
          <p className="text-emerald-100 mt-1">
            {items.length} товаров · Куплено {boughtCount} из {items.length}
          </p>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6">
        {/* Add Item Form */}
        <form onSubmit={handleAddItem} className="bg-white rounded-xl shadow p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={newItemName}
              onChange={(e) => setNewItemName(e.target.value)}
              placeholder="Название товара..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
            <select
              value={newItemCategory}
              onChange={(e) => setNewItemCategory(e.target.value)}
              className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              {Object.keys(CATEGORY_COLORS).map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            <button
              type="submit"
              className="bg-emerald-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-emerald-700 transition"
            >
              Добавить
            </button>
          </div>
        </form>

        {/* Error */}
        {error && (
          <div className="bg-red-50 text-red-700 border border-red-200 rounded-lg px-4 py-3 mb-4">
            {error}
          </div>
        )}

        {/* Items List */}
        {loading ? (
          <div className="text-center py-12 text-gray-500">Загрузка...</div>
        ) : items.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p className="text-xl mb-2">📝 Список пуст</p>
            <p className="text-sm">Добавьте товары вручную или отправьте список боту в Telegram</p>
          </div>
        ) : (
          <div className="space-y-3">
            {items.map((item) => (
              <div
                key={item.id}
                className={`bg-white rounded-xl shadow p-4 flex items-center gap-4 transition ${
                  item.is_bought ? 'opacity-60' : ''
                }`}
              >
                <input
                  type="checkbox"
                  checked={item.is_bought}
                  onChange={() => handleToggle(item)}
                  className="w-5 h-5 text-emerald-600 rounded focus:ring-emerald-500 cursor-pointer"
                />
                <div className="flex-1 min-w-0">
                  <p
                    className={`font-medium truncate ${
                      item.is_bought ? 'line-through text-gray-500' : ''
                    }`}
                  >
                    {item.name}
                  </p>
                  <span
                    className={`inline-block text-xs px-2 py-0.5 rounded-full mt-1 ${
                      CATEGORY_COLORS[item.category] || CATEGORY_COLORS['Другое']
                    }`}
                  >
                    {item.category}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Bot hint */}
        <div className="mt-8 bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center">
          <p className="text-emerald-700">
            💡 <strong>Совет:</strong> Напишите список покупок в Telegram-боте, и он автоматически добавит товары.
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;

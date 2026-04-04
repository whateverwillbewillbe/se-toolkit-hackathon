import { useState, useEffect, useCallback } from 'react';
import { getItems, createItem, toggleItem, deleteItem, clearItems, generateRecipe } from './api';
import './App.css';

const DEFAULT_USER_ID = Number(import.meta.env.VITE_DEFAULT_USER_ID) || 1;

const CATEGORY_EMOJIS = {
  'Vegetables': '🥕',
  'Fruits': '🍎',
  'Dairy': '🧀',
  'Meat': '🥩',
  'Grocery': '🌾',
  'Other': '📦',
};

const CATEGORY_ORDER = ['Vegetables', 'Fruits', 'Dairy', 'Meat', 'Grocery', 'Other'];

function App() {
  const [items, setItems] = useState([]);
  const [newItemName, setNewItemName] = useState('');
  const [newItemCategory, setNewItemCategory] = useState('Other');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recipe, setRecipe] = useState(null);
  const [recipeLoading, setRecipeLoading] = useState(false);
  const [showRecipeModal, setShowRecipeModal] = useState(false);
  const [toggling, setToggling] = useState(null);

  const fetchItems = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const { data } = await getItems(DEFAULT_USER_ID);
      setItems(data);
    } catch {
      setError('Failed to load shopping list');
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
      setNewItemCategory('Other');
    } catch {
      setError('Failed to add item');
    }
  };

  const handleToggle = async (item) => {
    setToggling(item.id);
    try {
      setError(null);
      const { data } = await toggleItem(item.id);
      setItems((prev) =>
        prev.map((it) => (it.id === item.id ? data : it))
      );
    } catch {
      setError('Failed to update status');
    } finally {
      setToggling(null);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Clear all items from your list?')) return;
    try {
      await clearItems(DEFAULT_USER_ID);
      setItems([]);
      setRecipe(null);
    } catch {
      setError('Failed to clear list');
    }
  };

  const handleDeleteItem = async (item) => {
    try {
      setError(null);
      await deleteItem(item.id);
      setItems((prev) => prev.filter((it) => it.id !== item.id));
    } catch {
      setError('Failed to delete item');
    }
  };

  const handleGenerateRecipe = async () => {
    setRecipeLoading(true);
    setError(null);
    try {
      const { data } = await generateRecipe(DEFAULT_USER_ID);
      setRecipe(data);
      setShowRecipeModal(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate recipe');
    } finally {
      setRecipeLoading(false);
    }
  };

  // Group items by category
  const itemsByCategory = {};
  items.forEach((item) => {
    if (!itemsByCategory[item.category]) {
      itemsByCategory[item.category] = [];
    }
    itemsByCategory[item.category].push(item);
  });

  const sortedCategories = CATEGORY_ORDER.filter((cat) => itemsByCategory[cat]);

  const boughtCount = items.filter((i) => i.is_bought).length;

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-emerald-600 text-white shadow-lg">
        <div className="max-w-2xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            🛒 My Groceries
          </h1>
          <p className="text-emerald-100 mt-1">
            {items.length} items · {boughtCount} bought
          </p>
          <div className="flex gap-3 mt-4">
            <button
              onClick={handleGenerateRecipe}
              disabled={recipeLoading || boughtCount === 0}
              className="bg-white/20 hover:bg-white/30 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-2 rounded-lg font-semibold transition text-sm"
            >
              {recipeLoading ? '✨ Cooking...' : '✨ Magic Recipe'}
            </button>
            {items.length > 0 && (
              <button
                onClick={handleClearAll}
                className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg font-semibold transition text-sm"
              >
                🗑️ Clear All
              </button>
            )}
          </div>
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
              placeholder="Item name..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
            <select
              value={newItemCategory}
              onChange={(e) => setNewItemCategory(e.target.value)}
              className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              {CATEGORY_ORDER.map((cat) => (
                <option key={cat} value={cat}>{CATEGORY_EMOJIS[cat]} {cat}</option>
              ))}
            </select>
            <button
              type="submit"
              className="bg-emerald-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-emerald-700 transition"
            >
              Add
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
          <div className="text-center py-12 text-gray-500">Loading...</div>
        ) : items.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p className="text-xl mb-2">📝 Your list is empty</p>
            <p className="text-sm">Add items manually or send a list to the Telegram bot</p>
          </div>
        ) : (
          <div className="space-y-6">
            {sortedCategories.map((category) => (
              <div key={category}>
                <h2 className="text-lg font-bold text-gray-800 mb-2 flex items-center gap-2">
                  {CATEGORY_EMOJIS[category] || '📦'} {category}
                  <span className="text-sm font-normal text-gray-400">
                    ({itemsByCategory[category].length})
                  </span>
                </h2>
                <div className="space-y-2">
                  {itemsByCategory[category].map((item) => (
                    <div
                      key={item.id}
                      className={`item-card bg-white rounded-xl shadow p-4 flex items-center gap-4 group ${
                        item.is_bought ? 'opacity-50' : ''
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={item.is_bought}
                        onChange={() => handleToggle(item)}
                        disabled={toggling === item.id}
                        className="w-5 h-5 text-emerald-600 rounded focus:ring-emerald-500 cursor-pointer"
                      />
                      <span
                        className={`flex-1 font-medium transition-all duration-300 ${
                          item.is_bought
                            ? 'line-through text-gray-400 item-bought'
                            : 'text-gray-900'
                        }`}
                      >
                        {item.name}
                      </span>
                      <button
                        onClick={() => handleDeleteItem(item)}
                        className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-500 transition-all duration-200 text-lg p-1"
                        title="Delete item"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Bot hint */}
        <div className="mt-8 bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center">
          <p className="text-emerald-700">
            💡 <strong>Tip:</strong> Write your shopping list in the Telegram bot and it will auto-add all items.
          </p>
        </div>
      </main>

      {/* Recipe Modal */}
      {showRecipeModal && recipe && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowRecipeModal(false)}
        >
          <div
            className="recipe-modal bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 animate-modal-in"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                👨‍🍳 {recipe.name || 'Mystery Dish'}
              </h2>
              <button
                onClick={() => setShowRecipeModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
              >
                ×
              </button>
            </div>
            <div className="space-y-3">
              {(recipe.steps || []).map((step, index) => (
                <div key={index} className="flex gap-3 items-start animate-step-in" style={{ animationDelay: `${index * 100}ms` }}>
                  <span className="bg-emerald-100 text-emerald-700 rounded-full w-7 h-7 flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {index + 1}
                  </span>
                  <p className="text-gray-700 pt-0.5">{step}</p>
                </div>
              ))}
            </div>
            <div className="mt-6 pt-4 border-t border-gray-200">
              <button
                onClick={() => setShowRecipeModal(false)}
                className="w-full bg-emerald-600 text-white py-2 rounded-lg font-semibold hover:bg-emerald-700 transition"
              >
                Enjoy! 🍽️
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

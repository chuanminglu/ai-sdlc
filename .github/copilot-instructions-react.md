---
applyTo: "**/*.jsx,**/*.tsx,**/*.js,**/*.ts"
---
# React Frontend Development Guidelines

Apply the [general coding guidelines](./copilot-instructions-general.md) and [TypeScript guidelines](./copilot-instructions-ts.md) to all code.

## React Component Guidelines

### Component Structure
```typescript
import React, { useState, useEffect } from 'react';
import { ComponentProps } from './types';
import styles from './Component.module.css';

interface Props {
  title: string;
  data?: ComponentProps[];
  onAction?: (id: string) => void;
}

export const Component: React.FC<Props> = ({ 
  title, 
  data = [], 
  onAction 
}) => {
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Side effects here
  }, []);
  
  const handleClick = (id: string) => {
    onAction?.(id);
  };
  
  return (
    <div className={styles.container}>
      <h2>{title}</h2>
      {/* Component JSX */}
    </div>
  );
};

export default Component;
```

### Hooks Guidelines
- Use functional components with hooks
- Extract custom hooks for reusable logic
- Follow hooks rules (no conditional calls)
- Use proper dependency arrays

```typescript
// Custom hook example
import { useState, useEffect } from 'react';

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useApi<T>(url: string): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchData();
  }, [url]);
  
  return { data, loading, error, refetch: fetchData };
}
```

### State Management
```typescript
// Context for global state
import React, { createContext, useContext, useReducer } from 'react';

interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  notifications: Notification[];
}

type AppAction = 
  | { type: 'SET_USER'; payload: User }
  | { type: 'SET_THEME'; payload: 'light' | 'dark' }
  | { type: 'ADD_NOTIFICATION'; payload: Notification };

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
} | null>(null);

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_THEME':
      return { ...state, theme: action.payload };
    case 'ADD_NOTIFICATION':
      return { 
        ...state, 
        notifications: [...state.notifications, action.payload] 
      };
    default:
      return state;
  }
}

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => {
  const [state, dispatch] = useReducer(appReducer, {
    user: null,
    theme: 'light',
    notifications: []
  });
  
  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};
```

## Styling Guidelines

### CSS Modules
```css
/* Component.module.css */
.container {
  padding: 1rem;
  border-radius: 8px;
  background-color: var(--bg-primary);
}

.title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  background-color: var(--color-primary);
  color: white;
  cursor: pointer;
  transition: background-color 0.2s;
}

.button:hover {
  background-color: var(--color-primary-dark);
}

.button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
```

### Styled Components (Alternative)
```typescript
import styled from 'styled-components';

const Container = styled.div`
  padding: 1rem;
  border-radius: 8px;
  background-color: ${props => props.theme.colors.background};
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  background-color: ${props => 
    props.variant === 'secondary' 
      ? props.theme.colors.secondary 
      : props.theme.colors.primary
  };
  color: white;
  cursor: pointer;
  
  &:hover {
    opacity: 0.8;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;
```

## Performance Optimization

### React.memo and useMemo
```typescript
import React, { memo, useMemo } from 'react';

interface Props {
  items: Item[];
  filter: string;
}

export const ItemList = memo<Props>(({ items, filter }) => {
  const filteredItems = useMemo(() => {
    return items.filter(item => 
      item.name.toLowerCase().includes(filter.toLowerCase())
    );
  }, [items, filter]);
  
  return (
    <ul>
      {filteredItems.map(item => (
        <ItemComponent key={item.id} item={item} />
      ))}
    </ul>
  );
});

// Only re-render if item changes
const ItemComponent = memo<{ item: Item }>(({ item }) => (
  <li>{item.name}</li>
));
```

### Lazy Loading
```typescript
import React, { Suspense, lazy } from 'react';

const LazyComponent = lazy(() => import('./LazyComponent'));

export const App: React.FC = () => {
  return (
    <div>
      <Suspense fallback={<div>Loading...</div>}>
        <LazyComponent />
      </Suspense>
    </div>
  );
};
```

## Form Handling

### React Hook Form
```typescript
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

const schema = yup.object().shape({
  name: yup.string().required('Name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  age: yup.number().min(0).max(150).required('Age is required')
});

interface FormData {
  name: string;
  email: string;
  age: number;
}

export const UserForm: React.FC = () => {
  const { 
    control, 
    handleSubmit, 
    formState: { errors, isSubmitting } 
  } = useForm<FormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      name: '',
      email: '',
      age: 0
    }
  });
  
  const onSubmit = async (data: FormData) => {
    try {
      await submitUser(data);
      // Handle success
    } catch (error) {
      // Handle error
    }
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Controller
        name="name"
        control={control}
        render={({ field }) => (
          <div>
            <input {...field} placeholder="Name" />
            {errors.name && <span>{errors.name.message}</span>}
          </div>
        )}
      />
      
      <Controller
        name="email"
        control={control}
        render={({ field }) => (
          <div>
            <input {...field} type="email" placeholder="Email" />
            {errors.email && <span>{errors.email.message}</span>}
          </div>
        )}
      />
      
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
};
```

## Testing

### Component Testing
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserForm } from './UserForm';

describe('UserForm', () => {
  it('should render form fields', () => {
    render(<UserForm />);
    
    expect(screen.getByPlaceholderText('Name')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument();
  });
  
  it('should show validation errors', async () => {
    render(<UserForm />);
    
    fireEvent.click(screen.getByRole('button', { name: 'Submit' }));
    
    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument();
      expect(screen.getByText('Email is required')).toBeInTheDocument();
    });
  });
  
  it('should submit form with valid data', async () => {
    const mockSubmit = jest.fn();
    // Mock the submit function
    
    render(<UserForm />);
    
    fireEvent.change(screen.getByPlaceholderText('Name'), {
      target: { value: 'John Doe' }
    });
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'john@example.com' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: 'Submit' }));
    
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com',
        age: 0
      });
    });
  });
});
```

## Accessibility Guidelines
- Use semantic HTML elements
- Provide proper ARIA labels
- Ensure keyboard navigation
- Maintain focus management
- Use sufficient color contrast
- Provide alternative text for images

```typescript
export const AccessibleButton: React.FC<{
  onClick: () => void;
  disabled?: boolean;
  ariaLabel?: string;
  children: React.ReactNode;
}> = ({ onClick, disabled, ariaLabel, children }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      aria-disabled={disabled}
      className={styles.button}
    >
      {children}
    </button>
  );
};
```

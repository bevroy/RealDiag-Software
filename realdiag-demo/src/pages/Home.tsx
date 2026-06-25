import { Link } from 'react-router-dom';
import { Play } from 'lucide-react';

export default function Home() {
  return (
    <div className='min-h-screen bg-slate-50 flex items-center justify-center p-6'>
      <div className='max-w-2xl text-center bg-white rounded-3xl shadow-lg border border-slate-200 p-10'>
        <h1 className='text-5xl font-bold text-slate-900'>RealDiag</h1>
        <p className='text-slate-600 mt-4 text-lg'>
          Probabilistic diagnostic support for faster, more accurate clinical decision-making.
        </p>
        <Link
          to='/demo'
          className='mt-8 inline-flex items-center gap-2 bg-teal-700 text-white px-6 py-3 rounded-xl font-semibold hover:bg-teal-800 transition'
        >
          <Play size={18} /> View Demo
        </Link>
      </div>
    </div>
  );
}

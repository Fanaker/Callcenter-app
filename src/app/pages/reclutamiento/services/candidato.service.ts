import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { Candidato } from '../models/candidato.model';
import { ReclutamientoValidadorService } from './reclutamiento-validador.service';

/**
 * Servicio de Candidatos
 * Gestiona todas las operaciones CRUD para candidatos
 */
@Injectable({
  providedIn: 'root'
})
export class CandidatoService {
  private apiUrl = 'http://localhost:3000/api/candidatos'; // Ajusta según tu backend

  private candidatosSubject = new BehaviorSubject<Candidato[]>([]);
  public candidatos$ = this.candidatosSubject.asObservable();

  private candidatoSeleccionadoSubject = new BehaviorSubject<Candidato | null>(null);
  public candidatoSeleccionado$ = this.candidatoSeleccionadoSubject.asObservable();

  constructor(
    private http: HttpClient,
    private validador: ReclutamientoValidadorService
  ) {
    this.cargarCandidatos();
  }

  /**
   * Carga todos los candidatos desde el servidor
   */
  cargarCandidatos(): void {
    this.http.get<Candidato[]>(this.apiUrl).subscribe({
      next: (candidatos) => {
        this.candidatosSubject.next(candidatos);
      },
      error: (error) => {
        console.error('Error al cargar candidatos:', error);
        // En caso de error, inicializa con array vacío
        this.candidatosSubject.next([]);
      }
    });
  }

  /**
   * Obtiene todos los candidatos
   */
  obtenerCandidatos(): Observable<Candidato[]> {
    return this.candidatos$;
  }

  /**
   * Obtiene un candidato por ID
   */
  obtenerCandidatoPorId(id: string): Observable<Candidato> {
    return this.http.get<Candidato>(`${this.apiUrl}/${id}`);
  }

  /**
   * Crea un nuevo candidato
   */
  crearCandidato(candidato: Candidato): Observable<Candidato> {
    return this.http.post<Candidato>(this.apiUrl, candidato).pipe(
      tap(() => this.cargarCandidatos())
    );
  }

  /**
   * Actualiza un candidato existente CON VALIDACIÓN
   * Asegura que si apto="no", entrevista se establezca a "no"
   */
  actualizarCandidato(id: string, candidato: Candidato): Observable<Candidato> {
    // Aplicar validación y corrección automática
    const candidatoCorregido = this.aplicarValidaciones(candidato);

    return this.http.put<Candidato>(`${this.apiUrl}/${id}`, candidatoCorregido).pipe(
      tap(() => {
        this.cargarCandidatos();
        this.candidatoSeleccionadoSubject.next(candidatoCorregido);
      })
    );
  }

  /**
   * Actualiza parcialmente un candidato (PATCH)
   */
  actualizarCandidatoParcial(id: string, cambios: Partial<Candidato>): Observable<Candidato> {
    // Convertir a candidato completo para validación
    const candidato = { ...cambios } as Candidato;
    const candidatoCorregido = this.aplicarValidaciones(candidato);

    return this.http.patch<Candidato>(`${this.apiUrl}/${id}`, candidatoCorregido).pipe(
      tap(() => {
        this.cargarCandidatos();
      })
    );
  }

  /**
   * Elimina un candidato
   */
  eliminarCandidato(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`).pipe(
      tap(() => this.cargarCandidatos())
    );
  }

  /**
   * Actualiza el campo Apto de un candidato
   */
  actualizarApto(id: string, valor: 'si' | 'no' | null): Observable<Candidato> {
    return this.actualizarCandidatoParcial(id, { apto: valor });
  }

  /**
   * Actualiza el campo Entrevista con validación
   * Si apto="no", la entrevista se fuerza a "no"
   */
  actualizarEntrevista(id: string, valor: 'si' | 'no' | null, aptoActual: 'si' | 'no' | null): Observable<Candidato> {
    const valorCorregido = this.validador.corregirEntrevista(aptoActual, valor);

    if (valorCorregido !== valor) {
      console.warn(`Entrevista ajustada de "${valor}" a "${valorCorregido}" según la regla de validación`);
    }

    return this.actualizarCandidatoParcial(id, { entrevista: valorCorregido });
  }

  /**
   * Obtiene candidatos filtrados por apto
   */
  obtenerCandidatosAptos(apto: 'si' | 'no'): Observable<Candidato[]> {
    return this.candidatos$.pipe(
      map(candidatos => candidatos.filter(c => c.apto === apto))
    );
  }

  /**
   * Obtiene candidatos que pasaron entrevista
   */
  obtenerCandidatosEntrevistados(resultado: 'si' | 'no'): Observable<Candidato[]> {
    return this.candidatos$.pipe(
      map(candidatos => candidatos.filter(c => c.entrevista === resultado))
    );
  }

  /**
   * Aplica las validaciones a un candidato
   */
  private aplicarValidaciones(candidato: Candidato): Candidato {
    const candidatoCorregido = { ...candidato };

    // Si apto es "no", forzar entrevista a "no"
    if (candidatoCorregido.apto === 'no') {
      candidatoCorregido.entrevista = 'no';
    }

    return candidatoCorregido;
  }

  /**
   * Obtiene el estado actual de un candidato con validación
   */
  obtenerEstadoValidacion(candidato: Candidato): {
    esValido: boolean;
    mensaje: string;
    cambiosAplicados: boolean;
  } {
    const valido = this.validador.validarAptoEntrevista(candidato.apto, candidato.entrevista);
    const corregido = this.validador.corregirEntrevista(candidato.apto, candidato.entrevista);

    return {
      esValido: valido,
      mensaje: valido ? '' : this.validador.obtenerMensajeError(candidato.apto),
      cambiosAplicados: corregido !== candidato.entrevista
    };
  }
}
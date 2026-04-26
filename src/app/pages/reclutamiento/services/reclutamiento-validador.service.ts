import { Injectable } from '@angular/core';

/**
 * Servicio de validación para reglas de reclutamiento
 *
 * REGLA: Solo se permite marcar entrevista como "Sí" cuando Apto = "Sí"
 * Si Apto = "No", la entrevista se debe forzar a "No" automáticamente
 */
@Injectable({
  providedIn: 'root'
})
export class ReclutamientoValidadorService {

  /**
   * Valida que la relación entre Apto y Entrevista sea válida
   *
   * @param apto - Valor del campo Apto ('si', 'no', null)
   * @param entrevista - Valor del campo Entrevista ('si', 'no', null)
   * @returns boolean - true si la combinación es válida
   */
  public validarAptoEntrevista(
    apto: 'si' | 'no' | null,
    entrevista: 'si' | 'no' | null
  ): boolean {
    // Si apto es "no", entrevista DEBE ser "no"
    if (apto === 'no' && entrevista !== 'no') {
      return false;
    }

    // Si apto es "si", entrevista puede ser cualquier valor
    if (apto === 'si') {
      return true;
    }

    // Si apto es null, entrevista debe ser null o "no"
    if (apto === null && entrevista === 'si') {
      return false;
    }

    return true;
  }

  /**
   * Corrige automáticamente el valor de entrevista según el apto
   *
   * @param apto - Valor del campo Apto
   * @param entrevista - Valor del campo Entrevista actual
   * @returns El valor de entrevista corregido
   */
  public corregirEntrevista(
    apto: 'si' | 'no' | null,
    entrevista: 'si' | 'no' | null
  ): 'si' | 'no' | null {
    // Si apto es "no", forzar entrevista a "no"
    if (apto === 'no') {
      return 'no';
    }

    // Si apto es null y entrevista es "si", cambiar a null
    if (apto === null && entrevista === 'si') {
      return null;
    }

    return entrevista;
  }

  /**
   * Obtiene el mensaje de error si la validación falla
   */
  public obtenerMensajeError(apto: 'si' | 'no' | null): string {
    if (apto === 'no') {
      return 'No puedes marcar "Sí" en Entrevista cuando Apto es "No". Se ha establecido automáticamente a "No".';
    }
    if (apto === null) {
      return 'Debes establecer Apto como "Sí" antes de marcar Entrevista como "Sí".';
    }
    return '';
  }

  /**
   * Determina si el campo de entrevista debe estar habilitado
   */
  public esEntrevistaHabilitada(apto: 'si' | 'no' | null): boolean {
    return apto === 'si';
  }

  /**
   * Obtiene el estado de la entrevista para mostrar en la UI
   */
  public obtenerEstadoEntrevista(
    apto: 'si' | 'no' | null,
    entrevista: 'si' | 'no' | null
  ): { habilitada: boolean; valor: 'si' | 'no' | null; razon: string } {
    const habilitada = this.esEntrevistaHabilitada(apto);
    const valorCorregido = this.corregirEntrevista(apto, entrevista);

    return {
      habilitada,
      valor: valorCorregido,
      razon: !habilitada ? 'Apto debe ser "Sí" para registrar entrevista' : ''
    };
  }
}
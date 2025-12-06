<?php
/**
 * Python Enerji Benchmark Sonuçlarını Okuma ve Veritabanına Aktarma
 * 
 * Bu dosya Python'da çalıştırılan enerji benchmark sonuçlarını okur
 * ve veritabanına kaydeder.
 */

// Yapılandırma
require_once __DIR__ . '/../config/database.php';

class EnergyBenchmarkImporter {
    
    private $pdo;
    private $resultsDir;
    
    public function __construct($pdo = null) {
        $this->pdo = $pdo ?? $GLOBALS['pdo'] ?? null;
        $this->resultsDir = __DIR__ . '/results';
    }
    
    /**
     * JSON dosyasından sonuçları oku
     */
    public function readResultsFile($filename) {
        $filepath = $this->resultsDir . '/' . $filename;
        
        if (!file_exists($filepath)) {
            return [
                'success' => false,
                'error' => "Dosya bulunamadı: {$filepath}"
            ];
        }
        
        $json = file_get_contents($filepath);
        $data = json_decode($json, true);
        
        if ($data === null) {
            return [
                'success' => false,
                'error' => 'JSON parse hatası: ' . json_last_error_msg()
            ];
        }
        
        return [
            'success' => true,
            'data' => $data
        ];
    }
    
    /**
     * En son benchmark dosyasını bul
     */
    public function getLatestResultFile() {
        if (!is_dir($this->resultsDir)) {
            return null;
        }
        
        $files = glob($this->resultsDir . '/energy_benchmark_*.json');
        
        if (empty($files)) {
            return null;
        }
        
        // En yeni dosyayı bul
        usort($files, function($a, $b) {
            return filemtime($b) - filemtime($a);
        });
        
        return basename($files[0]);
    }
    
    /**
     * Sonuçları veritabanına kaydet
     */
    public function saveToDatabase($data) {
        if (!$this->pdo) {
            return [
                'success' => false,
                'error' => 'Veritabanı bağlantısı yok'
            ];
        }
        
        try {
            // Tablo var mı kontrol et, yoksa oluştur
            $this->createTableIfNotExists();
            
            $meta = $data['meta'];
            $benchmarks = $data['benchmarks'];
            
            $stmt = $this->pdo->prepare("
                INSERT INTO python_energy_benchmarks 
                (algorithm_name, algorithm_type, data_size, 
                 execution_time_ms, energy_joules, power_watts,
                 comparisons, swaps, iterations, memory_accesses,
                 measurement_method, benchmark_timestamp, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())
            ");
            
            $insertedCount = 0;
            
            foreach ($benchmarks as $benchmark) {
                $avg = $benchmark['averages'];
                
                // En son run'dan metrikleri al
                $lastResult = end($benchmark['results']);
                $metrics = $lastResult['metrics'] ?? [];
                
                $stmt->execute([
                    $benchmark['algorithm'],
                    $benchmark['type'],
                    $benchmark['size'],
                    $avg['execution_time_ms'],
                    $avg['energy_joules'],
                    $avg['power_watts'],
                    $metrics['comparisons'] ?? 0,
                    $metrics['swaps'] ?? 0,
                    $metrics['iterations'] ?? 0,
                    $metrics['memory_accesses'] ?? 0,
                    $meta['measurement_method'],
                    $meta['timestamp']
                ]);
                
                $insertedCount++;
            }
            
            return [
                'success' => true,
                'inserted' => $insertedCount,
                'message' => "{$insertedCount} kayıt eklendi"
            ];
            
        } catch (PDOException $e) {
            return [
                'success' => false,
                'error' => 'Veritabanı hatası: ' . $e->getMessage()
            ];
        }
    }
    
    /**
     * Veritabanı tablosunu oluştur
     */
    private function createTableIfNotExists() {
        $sql = "
            CREATE TABLE IF NOT EXISTS python_energy_benchmarks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                algorithm_name VARCHAR(50) NOT NULL,
                algorithm_type VARCHAR(20) NOT NULL,
                data_size INT NOT NULL,
                execution_time_ms DOUBLE NOT NULL,
                energy_joules DOUBLE NOT NULL,
                power_watts DOUBLE NOT NULL,
                comparisons BIGINT DEFAULT 0,
                swaps BIGINT DEFAULT 0,
                iterations BIGINT DEFAULT 0,
                memory_accesses BIGINT DEFAULT 0,
                measurement_method VARCHAR(50) NOT NULL,
                benchmark_timestamp VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_algorithm (algorithm_name),
                INDEX idx_size (data_size),
                INDEX idx_timestamp (benchmark_timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ";
        
        $this->pdo->exec($sql);
    }
    
    /**
     * Özet istatistikleri getir
     */
    public function getSummaryStats() {
        if (!$this->pdo) {
            return ['error' => 'Veritabanı bağlantısı yok'];
        }
        
        $stmt = $this->pdo->query("
            SELECT 
                algorithm_name,
                algorithm_type,
                data_size,
                AVG(execution_time_ms) as avg_time,
                AVG(energy_joules) as avg_energy,
                AVG(power_watts) as avg_power,
                COUNT(*) as sample_count
            FROM python_energy_benchmarks
            GROUP BY algorithm_name, algorithm_type, data_size
            ORDER BY algorithm_type, data_size, algorithm_name
        ");
        
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
    
    /**
     * Belirli bir algoritma için sonuçları getir
     */
    public function getAlgorithmResults($algorithmName, $dataSize = null) {
        if (!$this->pdo) {
            return ['error' => 'Veritabanı bağlantısı yok'];
        }
        
        $sql = "SELECT * FROM python_energy_benchmarks WHERE algorithm_name = ?";
        $params = [$algorithmName];
        
        if ($dataSize !== null) {
            $sql .= " AND data_size = ?";
            $params[] = $dataSize;
        }
        
        $sql .= " ORDER BY created_at DESC LIMIT 100";
        
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);
        
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
    
    /**
     * Algoritma karşılaştırması için veri getir
     */
    public function getComparisonData($dataSize) {
        if (!$this->pdo) {
            return ['error' => 'Veritabanı bağlantısı yok'];
        }
        
        $stmt = $this->pdo->prepare("
            SELECT 
                algorithm_name,
                algorithm_type,
                AVG(execution_time_ms) as avg_time,
                AVG(energy_joules) as avg_energy,
                AVG(power_watts) as avg_power,
                AVG(comparisons) as avg_comparisons,
                AVG(swaps) as avg_swaps
            FROM python_energy_benchmarks
            WHERE data_size = ?
            GROUP BY algorithm_name, algorithm_type
            ORDER BY avg_energy ASC
        ");
        
        $stmt->execute([$dataSize]);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}

// API endpoint olarak kullanıldığında
if (basename($_SERVER['PHP_SELF']) === 'import_results.php') {
    header('Content-Type: application/json; charset=utf-8');
    
    $action = $_GET['action'] ?? 'import';
    $importer = new EnergyBenchmarkImporter();
    
    switch ($action) {
        case 'import':
            // En son dosyayı içe aktar
            $filename = $_GET['file'] ?? $importer->getLatestResultFile();
            
            if (!$filename) {
                echo json_encode(['error' => 'Hiç benchmark dosyası bulunamadı']);
                exit;
            }
            
            $result = $importer->readResultsFile($filename);
            
            if ($result['success']) {
                $saveResult = $importer->saveToDatabase($result['data']);
                echo json_encode($saveResult);
            } else {
                echo json_encode($result);
            }
            break;
            
        case 'summary':
            echo json_encode($importer->getSummaryStats());
            break;
            
        case 'compare':
            $size = (int)($_GET['size'] ?? 1000);
            echo json_encode($importer->getComparisonData($size));
            break;
            
        case 'list':
            // Mevcut dosyaları listele
            $files = glob(__DIR__ . '/results/energy_benchmark_*.json');
            $fileList = array_map('basename', $files);
            echo json_encode(['files' => $fileList]);
            break;
            
        default:
            echo json_encode(['error' => 'Geçersiz aksiyon']);
    }
}
